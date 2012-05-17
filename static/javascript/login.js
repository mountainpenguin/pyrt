$(document).ready(function () {
    $("#login_form").submit( function (e) {
        var hashed = hashPassword($("#password_input").val());
        var newinput = $("<input />").attr("type", "hidden").attr("name","password").val(hashed);
        $("#login_form").append(newinput);
        // set up persistent session
        computeSession($("#password_input").val());
        sess = getSession();
        var sessinput = $("<input />").attr("type", "hidden").attr("name", "persistentSession").val(sess);
        $("#login_form").append(sessinput);
    });
});

function getToken() {
    return Math.floor( (new Date().getTime() / 1000) / 10 );
}

function getPermSalt() {
    return $("#permanent_salt").val();
}

function genSalt() {
    var salt = new String();
    for (i=0; i<10; i++) {
        var r = Math.floor( Math.random() * 128 );
        salt += String.fromCharCode(r);
    }
    return window.btoa(salt);
}

function hashPassword(pw) {
    var new_salt = genSalt();
    var token = getToken();
    var token_salt = CryptoJS.SHA256(token + new_salt);
    var hashed1 = CryptoJS.SHA256(pw);
    var hashed2 = CryptoJS.SHA256(hashed1 + getPermSalt());
    var hashed3 = CryptoJS.SHA256(hashed2 + token_salt);
    return "$" + new_salt + "$" + hashed3;
}

function computeHP(pw) {
    var new_salt = genSalt();
    var hashed1 = CryptoJS.SHA256(pw);
    var hashed2 = CryptoJS.SHA256(hashed1 + getPermSalt());
    var hashed3 = CryptoJS.SHA256(hashed2 + new_salt);
    return new Array(new_salt, hashed3);
}

function computeSession(pw) {
    var pSess = computeHP(pw);
    // save session
    sessionStorage.persistentSession = "$" + pSess[0] + "$" + pSess[1];
}

function getSession() {
    if (sessionStorage.persistentSession) {
        var pSess = sessionStorage.persistentSession.split("$").slice(1);
    } else {
        var pSess = new Array("", "");
    }
    var token = getToken();
    var token_salt = CryptoJS.SHA256(token + pSess[0]);
    var pSess_OTP = CryptoJS.SHA256(pSess[1] + token_salt);
    return "$" + pSess[0] + "$" + pSess_OTP;
}
