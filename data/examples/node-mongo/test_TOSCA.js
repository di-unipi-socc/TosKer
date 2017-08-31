// jshint esversion: 6, asi:true

/**
    app DEFINITION
**/
app = tk.Software('app')
    .artifacts('app/{main.js,package.json}')
    .interfaces([
        create,
        start,
        stop,
        del
    ])
    .host(node)
    .connection(db)

create = tk.Interface('create', () => {
    tk.exec('npm install')
})
start = tk.Interface('start', () => {
    tk.export('PORT', 80)
    tk.exec('node main.js')
})
stop = tk.Interface('stop', start.revert())
del = tk.Interface('delete', create.revert())

/**
    node DEFINITION
**/
node = tk.Software('node')
    .interfaces([
        tk.Interface('create', 'install_node.sh')
    ])
    .host(server1)

/**
    server1 DEFINITION
**/
server1 = tk.Container('server1')
    .port(80, 8080)
    .image('ubuntu:latest')

/**
    db DEFINITION
**/
db = tk.Container('db')
    .image('mongo:latest')

tk.template(app, db, node, server1)
