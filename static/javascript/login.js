$(document).ready(function () {
    $("#login_form").submit( function (e) {
        //e.preventDefault();
        var hashed = hashPassword($("#password_input").val());
        var newinput = $("<input />").attr("type", "hidden").attr("name","password").val(hashed);
        $("#login_form").append(newinput);
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
    console.log("new_salt", new_salt);
    var token = getToken();
    console.log("token", token);
    var token_salt = CryptoJS.SHA256(token + new_salt);
    console.log("token_salt", token_salt);
    
    var hashed1 = CryptoJS.SHA256(pw);
    console.log("hashed1", hashed1);
    var hashed2 = CryptoJS.SHA256(hashed1 + getPermSalt());
    console.log("hashed2", hashed2);
    var hashed3 = CryptoJS.SHA256(hashed2 + token_salt);
    console.log("hashed3", hashed3);
    
    console.log("final: $" + new_salt + "$" + hashed3);
    return "$" + new_salt + "$" + hashed3;
}