import json, ldap3

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
groups = test.search("ou=group,dc=sanger,dc=ac,dc=uk", "(objectClass=sangerHumgenProjectGroup)",
 ldap3.LEVEL, ['cn', 'memberUid'])

with open('sync/ldap-humgen-groups-users.json', 'w') as file:
    str = "["
    for group in groups:
        group_str = json.dumps(group)
        str += group_str + ","
    str = str.rstrip(',') + "]"
    file.write(str)
