def apply(store):
    store.execute("""ALTER TABLE stations CHANGE BroadcastDeleted BroadcastRemoved BIGINT DEFAULT NULL COMMENT 'last removal of an associated broadcast'""")
    store.execute("""ALTER TABLE broadcasts CHANGE TransmissionDeleted TransmissionRemoved BIGINT DEFAULT NULL COMMENT 'last removal of an associated transmission'""")
