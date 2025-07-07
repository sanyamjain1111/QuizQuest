from functools import wraps
from flask import request, jsonify, make_response
from flask_jwt_extended import get_jwt_identity
import hashlib
import json

def generate_cache_key(*args, **kwargs):
    """Generate a consistent cache key from request data"""
    path = request.path
    args_str = str(sorted(request.args.items()))
    body = request.get_data(as_text=True) if request.method in ['POST', 'PUT', 'PATCH'] else ''
    
    # Include user identity in key if authenticated
    try:
        user_identity = get_jwt_identity() or 'anonymous'
    except:
        user_identity = 'anonymous'
    
    key_data = f"{user_identity}:{path}:{args_str}:{body}"
    return hashlib.md5(key_data.encode()).hexdigest()

def cached(timeout=None, key_prefix='view_', unless=None):
    """
    Decorator to cache view responses.
    
    Args:
        timeout: Cache timeout in seconds (defaults to config.CACHE_TIMEOUT)
        key_prefix: Prefix for cache keys
        unless: Callable that returns True if caching should be skipped
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import current_app
            
            # Skip cache if unless condition is met
            if unless and unless():
                return f(*args, **kwargs)
                
            cache_key = f"{key_prefix}{generate_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            try:
                cache = current_app.extensions.get('cache')
                if not cache:
                    # Cache not available, skip caching
                    return f(*args, **kwargs)
                
                cached_data = cache.get(cache_key)
                if cached_data is not None:
                    return jsonify(cached_data)
            except Exception as e:
                current_app.logger.error(f"Cache get error: {str(e)}")
                # If cache fails, continue without caching
                return f(*args, **kwargs)
            
            # Execute function if not in cache
            response = f(*args, **kwargs)
            
            # Handle different response types
            status_code = 200  # default
            response_data = None
            
            if isinstance(response, tuple):
                # It's a tuple - could be (jsonify_response, status) or (data, status, headers)
                first_item = response[0]
                status_code = response[1] if len(response) >= 2 else 200
                
                # Check if first item is a Response object (from jsonify)
                if hasattr(first_item, 'get_json') and hasattr(first_item, 'status_code'):
                    # It's a jsonify response object
                    try:
                        response_data = first_item.get_json()
                        # Use the status code from the Response object, not the tuple
                        status_code = first_item.status_code
                    except:
                        response_data = None
                else:
                    # It's raw data
                    response_data = first_item
                    
            elif hasattr(response, 'status_code'):
                # It's already a Response object
                status_code = response.status_code
                try:
                    response_data = response.get_json()
                except:
                    response_data = None
            else:
                # It's just data
                response_data = response
            
            # Only cache successful responses with valid data
            if status_code == 200 and response_data is not None and cache:
                try:
                    # Check if cache has the set method
                    if hasattr(cache, 'set'):
                        cache.set(cache_key, response_data, timeout=timeout)
                    else:
                        current_app.logger.warning("Cache object doesn't have 'set' method")
                except Exception as e:
                    current_app.logger.error(f"Cache set error: {str(e)}")
            
            return response
        return decorated_function
    return decorator

def invalidate_cache(pattern):
    """
    Decorator to invalidate cache entries matching a pattern.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import current_app
            
            # First execute the function
            response = f(*args, **kwargs)
            
            # Handle different response types for status code check
            status_code = 200
            if isinstance(response, tuple):
                first_item = response[0]
                if hasattr(first_item, 'status_code'):
                    # First item is a Response object (from jsonify)
                    status_code = first_item.status_code
                elif len(response) >= 2:
                    # Traditional tuple (data, status_code)
                    status_code = response[1]
            elif hasattr(response, 'status_code'):
                status_code = response.status_code
            
            # Then invalidate cache if successful
            if status_code in [200, 201, 204]:
                try:
                    cache = current_app.extensions.get('cache')
                    if not cache:
                        return response
                    
                    # Try to clear cache entries matching pattern
                    if hasattr(cache, 'cache') and hasattr(cache.cache, '_client'):
                        # Redis backend
                        keys = []
                        cursor = '0'
                        cache_prefix = current_app.config.get('CACHE_KEY_PREFIX', 'flask_cache_')
                        while cursor != 0:
                            cursor, partial_keys = cache.cache._client.scan(
                                cursor=cursor,
                                match=f"{cache_prefix}*{pattern}*"
                            )
                            keys.extend(partial_keys)
                        
                        if keys:
                            cache.delete_many(*[key.decode() if isinstance(key, bytes) else key for key in keys])
                    else:
                        # Simple backend - clear all cache (not ideal but safe)
                        cache.clear()
                except Exception as e:
                    current_app.logger.error(f"Cache invalidation error: {str(e)}")
            
            return response
        return decorated_function
    return decorator

def cache_invalidate_single(key_template):
    """
    Decorator to invalidate a specific cache key after write operations.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import current_app
            
            # First execute the function
            response = f(*args, **kwargs)
            
            # Handle different response types for status code check
            status_code = 200
            if isinstance(response, tuple):
                first_item = response[0]
                if hasattr(first_item, 'status_code'):
                    # First item is a Response object (from jsonify)
                    status_code = first_item.status_code
                elif len(response) >= 2:
                    # Traditional tuple (data, status_code)
                    status_code = response[1]
            elif hasattr(response, 'status_code'):
                status_code = response.status_code
            
            # Then invalidate specific cache if successful
            if status_code in [200, 201, 204]:
                try:
                    cache = current_app.extensions.get('cache')
                    if cache and hasattr(cache, 'delete'):
                        cache_key = key_template.format(**kwargs)
                        cache.delete(cache_key)
                except Exception as e:
                    current_app.logger.error(f"Cache invalidation error: {str(e)}")
            
            return response
        return decorated_function
    return decorator