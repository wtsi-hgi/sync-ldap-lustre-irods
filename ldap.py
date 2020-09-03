import ldap3

class LDAP():
    _server:ldap3.Server
    _conn:ldap3.Connection

    def __init__(self):
        self._server = ldap3.Server(host='ldap-ro.internal.sanger.ac.uk', port=389)
        self._conn = ldap3.Connection(self._server, lazy = True, read_only= True, authentication=ldap3.ANONYMOUS)

    def search(self, dn, query, scope, attr):
        with self._conn as ldap:
            ldap.search(search_base=dn, search_filter =query,
                search_scope=scope, attributes=attr)
            return(entry.entry_attributes_as_dict for entry in ldap.entries)

test = LDAP()
groups = test.search("ou=group,dc=sanger,dc=ac,dc=uk", "(objectClass=sangerHumgenProjectGroup)", ldap3.LEVEL, ['cn', 'memberUid'])
print(groups)
for group in groups:
    print(group)
    users = test.search("ou=people,dc=sanger,dc=ac,dc=uk", "(uid={g})".format(g=group), ldap3.LEVEL, ldap3.ALL_ATTRIBUTES)
