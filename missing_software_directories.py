import json, ldap3, subprocess, os

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

groups = test.search("ou=group,dc=sanger,dc=ac,dc=uk",
                     "(objectClass=sangerHumgenProjectGroup)",
                     ldap3.LEVEL, ['cn', 'memberUid'])

list_humgen_members = []
for group in groups:
    for humgen_member in group['memberUid']:
        list_humgen_members.append(humgen_member)
        
list_humgen_members = set(list_humgen_members)
n_humgen_members = len(list_humgen_members)
print ("Number of members from LDAP groups search (objectClass=sangerHumgenProjectGroup): ", str(n_humgen_members))


n = 1
list_humgen_members_gids = []
for humgen_member in list_humgen_members:
    # similar to cli search:
    #   ldapsearch -h ldap-ro.internal.sanger.ac.uk -p 389 -b "dc=sanger,dc=ac,dc=uk" -x "(uid=gn5)"
    # cf. wiki http://mediawiki.internal.sanger.ac.uk/index.php/LDAP
    # cf. LDAP()..search doc https://ldap3.readthedocs.io/en/latest/searches.html
    print(str(n) + '/' + str(n_humgen_members) + ' getting default group of user ' + humgen_member) 
    ldap_gids = test.search("dc=sanger,dc=ac,dc=uk",
                           "(&(sangerAgressoCurrentPerson=Yes)(sangerRealPerson=TRUE)(uid=" + humgen_member  +"))",
                            ldap3.SUBTREE, ['uid', 'gidNumber']) # ldap3.ALL_ATTRIBUTES) 
    n = n + 1
    for ldap_gid in ldap_gids:
        list_humgen_members_gids.append(ldap_gid['gidNumber'][0])
        
list_humgen_members_gids = set(list_humgen_members_gids)
n_list_humgen_members_gids = len(list_humgen_members_gids)
print ("Number of gidNumber retrieved for all humgen members: ", str(n_list_humgen_members_gids))
print (list_humgen_members_gids)

groups = []
for gid in list_humgen_members_gids:
    result = subprocess.run(['getent', 'group', str(gid)], stdout=subprocess.PIPE)
    group = result.stdout.decode('utf-8').split(':')[0]
    groups.append(group)
    
groups = [x for x in set(groups) if x]
n_groups = len(groups)
print ("Number of groups: ", str(n_groups))
print(groups)

software_subdirectories = next(os.walk('/software'))[1]
missing_directories = [x for x in groups if x not in software_subdirectories]
# excluding obvious names:
to_exclude = ['humgen','systemd-network','deleted_usr','cancer','ssg','cancer-pipeline',
              'ssg','cellgeni','toladmin','vr-impute', 'ssg-isg']
missing_directories = [x for x in missing_directories if x not in to_exclude]
n_missing_directories = len(missing_directories)
print ("n missing group directories in /software: ", str(n_missing_directories))
print(missing_directories)

with open("missing_software_directories.txt", 'w') as f:
    f.write("\n".join(map(str, missing_directories)))
