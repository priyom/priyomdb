def apply(store):
    store.execute("""ALTER TABLE stations DROP KEY BroadcastDeleted""")
    store.execute("""ALTER TABLE stations ADD INDEX (BroadcastRemoved)""")
    
    store.execute("""ALTER TABLE broadcasts DROP KEY TransmissionDeleted""")
    store.execute("""ALTER TABLE broadcasts ADD INDEX (TransmissionRemoved)""")
