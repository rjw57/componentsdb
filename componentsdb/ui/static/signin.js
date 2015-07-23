function getMetaTagContent(name) {
    var elements = document.getElementsByTagName('meta');
    for(var i=0; i<elements.length; i++) {
        var e = elements.item(i);
        if(e.name === name) {
            return e.content;
        }
    }
    return null;
}

function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
        console.log('User signed out.');
    });
}

function onSignIn(googleUser) {
    var token = googleUser.getAuthResponse().id_token,
        url = getMetaTagContent('google-token-exchange-url');

    console.log('signed in with id: ' + googleUser.getId());
    console.log('auth token: ' + token);

    if(url.indexOf('?') == -1) {
        url += '?token=' + encodeURIComponent(token);
    } else {
        url += '&token=' + encodeURIComponent(token);
    }
    console.log('exchange URL: ' + url);

    document.location.assign(url);
}

