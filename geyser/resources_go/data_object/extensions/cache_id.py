#!/usr/bin/env python
# coding=utf-8
from item import Item
from resources_go.types import go_types


class CacheID( Item ):
    def __init__( self, data ):
        super( CacheID, self ).__init__( "", data )

    def getNative( self, go_compiler ):
        return
        service = go_compiler.service.Name()
        module = self.parent.Name()

        param_full = "name string"
        param = "name"

        gofile = go_compiler.srv_api_package.addGoFile( "{service}.{module}.id".format( service = service,
                                                                                        module = module.lower() ),
                                                        only_create = True )
        gofile.addImport( "fmt" )
        gofile.addImport( "core" )
        gofile.addImport( "sync" )

        # cache
        value = "map[string]int<@@>"
        cache_name = "{}_cache".format( module )
        gofile.addVar(cache_name, value, go_types.text_array)
        # mutex
        mvalue = "sync.Mutex<@@>"
        mutex_name = "{}_mutex".format( module )
        gofile.addVar(mutex_name, mvalue, go_types.text_array)

        collection_name = '"id:{service}:{module}"'.format( service = service,
                                                            module = module )
        collection_var = "id_{module}_collection".format( module = module )
        gofile.addVar( collection_var, collection_name )

        # get key
        get_key_fu = gofile.addFunction( "get{}Key".format( module.capitalize() ) )
        get_key_fu.addArgs( param_full )
        get_key_fu.addResults( "string" )
        body = '''    res := {param}
    return res'''.format( param = param )
        get_key_fu.addBody( body )

        # get id cache
        get_id_cache = gofile.addFunction( "Get{}IdCache".format( module.capitalize() ) )
        get_id_cache.addArgs( param_full )
        get_id_cache.addResults( "int, bool" )

        body = '''    key := get{module_up}Key({param})
    if id, ok := {module}_cache[key]; ok <@
        return id, true
    @> else <@
        if id, ok := core.GetIdStorage({collection}, key); ok <@
            {module}_mutex.Lock()
            {module}_cache[key] = id
            {module}_mutex.Unlock()
            core.PublishInfo(fmt.Sprintf("{module}: get_{module}_id: get id from db: key: %v", key))
            return id, true
        @>
        return 0, false
    @>'''.format( module = module,
                  module_up = module.capitalize(),
                  param = param,
                  collection = collection_var )
        get_id_cache.addBody( body )

        # get id invoke call
    #     get_id_cache_invoke = gofile.addFunction( "Get{}IdCacheInvokeCall".format( module.capitalize() ) )
    #     get_id_cache_invoke.addArgs( param_full )
    #     get_id_cache_invoke.addResults( "int, error" )
    #
    #     body = '''    if id, ok := Get{module_up}IdCache({param}); ok <@
    #     return id, nil
    # @> else <@
    #     id, err := Get{module_up}Id({param})
    #     if err != nil <@
    #         return id, err
    #     @>
    #
    #     key := get{module_up}Key({param})
    #     {module}_cache[key] = id
    #
    #     return id, nil
    # @>'''.format( module = module,
    #               module_up = module.capitalize(),
    #               collection = collection_var,
    #               param = param )
    #     get_id_cache_invoke.addBody( body )
    #
    #     # get id async call
    #     get_id_cache_async = gofile.addFunction( "Get{}IdCacheAsyncCall".format( module.capitalize() ) )
    #     get_id_cache_async.addArgs( param_full )
    #     get_id_cache_async.addResults( "int, error" )
    #
    #     body = '''    if id, ok := Get{module_up}IdCache({param}); ok <@
    #     return id, nil
    # @> else <@
    #     id, err := Get{module_up}IdAsync({param})
    #     if err != nil <@
    #         return id, err
    #     @>
    #
    #     key := get{module_up}Key({param})
    #     {module}_cache[key] = id
    #
    #     return id, nil
    # @>'''.format( module = module,
    #               module_up = module.capitalize(),
    #               collection = collection_var,
    #               param = param )
    #     get_id_cache_async.addBody( body )

        # set pair id storage
        set_id_storage = gofile.addFunction( "Set{}IdStorage".format( module.capitalize() ) )
        set_id_storage.addArgs( param_full + ", id int" )

        body = '''    key := get{module_up}Key({param})
            core.SetIdStorage(id_{module}_collection, key, id)'''.format( module = module,
                                                                          module_up = module.capitalize(),
                                                                          param = param )
        set_id_storage.addBody( body )
