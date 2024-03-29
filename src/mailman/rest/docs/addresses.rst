=========
Addresses
=========

The REST API can be used to manage addresses.

There are no addresses yet.

    >>> dump_json('http://localhost:9001/3.0/addresses')
    http_etag: "..."
    start: 0
    total_size: 0

When an address is created via the internal API, it is available in the REST
API.
::

    >>> from zope.component import getUtility
    >>> from mailman.interfaces.usermanager import IUserManager
    >>> user_manager = getUtility(IUserManager)
    >>> anne = user_manager.create_address('anne@example.com')
    >>> transaction.commit()

    >>> dump_json('http://localhost:9001/3.0/addresses')
    entry 0:
        email: anne@example.com
        http_etag: "..."
        original_email: anne@example.com
        registered_on: 2005-08-01T07:49:23
        self_link: http://localhost:9001/3.0/addresses/anne@example.com
    http_etag: "..."
    start: 0
    total_size: 1

Anne's address can also be accessed directly.

    >>> dump_json('http://localhost:9001/3.0/addresses/anne@example.com')
    email: anne@example.com
    http_etag: "..."
    original_email: anne@example.com
    registered_on: 2005-08-01T07:49:23
    self_link: http://localhost:9001/3.0/addresses/anne@example.com

Bart registers with a mixed-case address.  The canonical URL always includes
the lower-case version.

    >>> bart = user_manager.create_address('Bart.Person@example.com')
    >>> transaction.commit()
    >>> dump_json(
    ...     'http://localhost:9001/3.0/addresses/bart.person@example.com')
    email: bart.person@example.com
    http_etag: "..."
    original_email: Bart.Person@example.com
    registered_on: 2005-08-01T07:49:23
    self_link: http://localhost:9001/3.0/addresses/bart.person@example.com

But his address record can be accessed with the case-preserved version too.

    >>> dump_json(
    ...     'http://localhost:9001/3.0/addresses/Bart.Person@example.com')
    email: bart.person@example.com
    http_etag: "..."
    original_email: Bart.Person@example.com
    registered_on: 2005-08-01T07:49:23
    self_link: http://localhost:9001/3.0/addresses/bart.person@example.com

A non-existent email address can't be retrieved.

    >>> dump_json('http://localhost:9001/3.0/addresses/nobody@example.com')
    Traceback (most recent call last):
    ...
    HTTPError: HTTP Error 404: 404 Not Found

When an address has a real name associated with it, this is also available in
the REST API.

    >>> cris = user_manager.create_address('cris@example.com', 'Cris Person')
    >>> transaction.commit()
    >>> dump_json('http://localhost:9001/3.0/addresses/cris@example.com')
    display_name: Cris Person
    email: cris@example.com
    http_etag: "..."
    original_email: cris@example.com
    registered_on: 2005-08-01T07:49:23
    self_link: http://localhost:9001/3.0/addresses/cris@example.com


Verifying
=========

When the address gets verified, this attribute is available in the REST
representation.

    >>> from mailman.utilities.datetime import now
    >>> anne.verified_on = now()
    >>> transaction.commit()
    >>> dump_json('http://localhost:9001/3.0/addresses/anne@example.com')
    email: anne@example.com
    http_etag: "..."
    original_email: anne@example.com
    registered_on: 2005-08-01T07:49:23
    self_link: http://localhost:9001/3.0/addresses/anne@example.com
    verified_on: 2005-08-01T07:49:23

Addresses can also be verified through the REST API, by POSTing to the
'verify' sub-resource.  The POST data is ignored.

    >>> dump_json('http://localhost:9001/3.0/addresses/'
    ...           'cris@example.com/verify', {})
    content-length: 0
    date: ...
    server: ...
    status: 204

Now Cris's address is verified.

    >>> dump_json('http://localhost:9001/3.0/addresses/cris@example.com')
    display_name: Cris Person
    email: cris@example.com
    http_etag: "..."
    original_email: cris@example.com
    registered_on: 2005-08-01T07:49:23
    self_link: http://localhost:9001/3.0/addresses/cris@example.com
    verified_on: 2005-08-01T07:49:23

If you should ever need to 'unverify' an address, POST to the 'unverify'
sub-resource.  Again, the POST data is ignored.

    >>> dump_json('http://localhost:9001/3.0/addresses/'
    ...           'cris@example.com/unverify', {})
    content-length: 0
    date: ...
    server: ...
    status: 204

Now Cris's address is unverified.

    >>> dump_json('http://localhost:9001/3.0/addresses/cris@example.com')
    display_name: Cris Person
    email: cris@example.com
    http_etag: "..."
    original_email: cris@example.com
    registered_on: 2005-08-01T07:49:23
    self_link: http://localhost:9001/3.0/addresses/cris@example.com


User addresses
==============

Users control addresses.  The canonical URLs for these user-controlled
addresses live in the /addresses namespace.
::

    >>> dave = user_manager.create_user('dave@example.com', 'Dave Person')
    >>> transaction.commit()
    >>> dump_json('http://localhost:9001/3.0/users/dave@example.com/addresses')
    entry 0:
        display_name: Dave Person
        email: dave@example.com
        http_etag: "..."
        original_email: dave@example.com
        registered_on: 2005-08-01T07:49:23
        self_link: http://localhost:9001/3.0/addresses/dave@example.com
    http_etag: "..."
    start: 0
    total_size: 1

    >>> dump_json('http://localhost:9001/3.0/addresses/dave@example.com')
    display_name: Dave Person
    email: dave@example.com
    http_etag: "..."
    original_email: dave@example.com
    registered_on: 2005-08-01T07:49:23
    self_link: http://localhost:9001/3.0/addresses/dave@example.com

A user can be associated with multiple email addresses.  You can add new
addresses to an existing user.

    >>> dump_json(
    ...     'http://localhost:9001/3.0/users/dave@example.com/addresses', {
    ...           'email': 'dave.person@example.org'
    ...           })
    content-length: 0
    date: ...
    location: http://localhost:9001/3.0/addresses/dave.person@example.org
    server: ...
    status: 201

When you add the new address, you can give it an optional display name.

    >>> dump_json(
    ...     'http://localhost:9001/3.0/users/dave@example.com/addresses', {
    ...           'email': 'dp@example.org',
    ...           'display_name': 'Davie P',
    ...           })
    content-length: 0
    date: ...
    location: http://localhost:9001/3.0/addresses/dp@example.org
    server: ...
    status: 201

The user controls these new addresses.

    >>> dump_json('http://localhost:9001/3.0/users/dave@example.com/addresses')
    entry 0:
        email: dave.person@example.org
        http_etag: "..."
        original_email: dave.person@example.org
        registered_on: 2005-08-01T07:49:23
        self_link: http://localhost:9001/3.0/addresses/dave.person@example.org
    entry 1:
        display_name: Dave Person
        email: dave@example.com
        http_etag: "..."
        original_email: dave@example.com
        registered_on: 2005-08-01T07:49:23
        self_link: http://localhost:9001/3.0/addresses/dave@example.com
    entry 2:
        display_name: Davie P
        email: dp@example.org
        http_etag: "..."
        original_email: dp@example.org
        registered_on: 2005-08-01T07:49:23
        self_link: http://localhost:9001/3.0/addresses/dp@example.org
    http_etag: "..."
    start: 0
    total_size: 3


Memberships
===========

Addresses can be subscribed to mailing lists.  When they are, all the
membership records for that address are easily accessible via the REST API.

Elle registers several email addresses.

    >>> elle = user_manager.create_user('elle@example.com', 'Elle Person')
    >>> subscriber = list(elle.addresses)[0]
    >>> elle.register('eperson@example.com')
    <Address: eperson@example.com [not verified] at ...>
    >>> elle.register('elle.person@example.com')
    <Address: elle.person@example.com [not verified] at ...>

Elle subscribes to two mailing lists with one of her addresses.
::

    >>> ant = create_list('ant@example.com')
    >>> bee = create_list('bee@example.com')
    >>> ant.subscribe(subscriber)
    <Member: Elle Person <elle@example.com> on ant@example.com
             as MemberRole.member>
    >>> bee.subscribe(subscriber)
    <Member: Elle Person <elle@example.com> on bee@example.com
             as MemberRole.member>
    >>> transaction.commit()

Elle can get her memberships for each of her email addresses.
::

    >>> dump_json('http://localhost:9001/3.0/addresses/'
    ...           'elle@example.com/memberships')
    entry 0:
        address: http://localhost:9001/3.0/addresses/elle@example.com
        delivery_mode: regular
        email: elle@example.com
        http_etag: "..."
        list_id: ant.example.com
        role: member
        self_link: http://localhost:9001/3.0/members/1
        user: http://localhost:9001/3.0/users/2
    entry 1:
        address: http://localhost:9001/3.0/addresses/elle@example.com
        delivery_mode: regular
        email: elle@example.com
        http_etag: "..."
        list_id: bee.example.com
        role: member
        self_link: http://localhost:9001/3.0/members/2
        user: http://localhost:9001/3.0/users/2
    http_etag: "..."
    start: 0
    total_size: 2

    >>> dump_json('http://localhost:9001/3.0/addresses/'
    ...           'eperson@example.com/memberships')
    http_etag: "..."
    start: 0
    total_size: 0

When Elle subscribes to the `bee` list again with a different address, this
does not show up in the list of memberships for his other address.
::

    >>> subscriber = user_manager.get_address('eperson@example.com')
    >>> bee.subscribe(subscriber)
    <Member: eperson@example.com on bee@example.com as MemberRole.member>
    >>> transaction.commit()

    >>> dump_json('http://localhost:9001/3.0/addresses/'
    ...           'elle@example.com/memberships')
    entry 0:
        address: http://localhost:9001/3.0/addresses/elle@example.com
        delivery_mode: regular
        email: elle@example.com
        http_etag: "..."
        list_id: ant.example.com
        role: member
        self_link: http://localhost:9001/3.0/members/1
        user: http://localhost:9001/3.0/users/2
    entry 1:
        address: http://localhost:9001/3.0/addresses/elle@example.com
        delivery_mode: regular
        email: elle@example.com
        http_etag: "..."
        list_id: bee.example.com
        role: member
        self_link: http://localhost:9001/3.0/members/2
        user: http://localhost:9001/3.0/users/2
    http_etag: "..."
    start: 0
    total_size: 2

    >>> dump_json('http://localhost:9001/3.0/addresses/'
    ...           'eperson@example.com/memberships')
    entry 0:
        address: http://localhost:9001/3.0/addresses/eperson@example.com
        delivery_mode: regular
        email: eperson@example.com
        http_etag: "..."
        list_id: bee.example.com
        role: member
        self_link: http://localhost:9001/3.0/members/3
        user: http://localhost:9001/3.0/users/2
    http_etag: "..."
    start: 0
    total_size: 1
