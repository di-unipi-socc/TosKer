// jshint esversion: 6, asi:true

tk.states(
    'created',
    'started',
    'deleted'
)

tk.interfaces(
    create,
    start,
    stop,
    del
)

create = tk.interface('create', () => {
        tk.exec('npm install')
    })
    .go('deleted', 'started')

start = tk.interface('start', () => {
        tk.export('PORT', 80)
        tk.exec('node main.js')
    })
    .require('db', 'started')
    .go('created', 'started')

stop = tk.interface('stop', start.revert())
    .go('started', 'created')

del = tk.interface('delete', create.revert())
    .go('created', 'deleted')
