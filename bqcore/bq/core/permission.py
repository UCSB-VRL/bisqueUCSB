
PUBLIC=0
PRIVATE=1
perm2str = {
    PUBLIC : 'published',
    PRIVATE : 'private'
}
perm2code =  dict((v,k) for k, v in perm2str.iteritems())
