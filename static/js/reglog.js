function createUser() {
    const username = document.getElementById("create-username");
    const password = document.getElementById("create-password");
    console.log(password, username)

    data = {
        'username': username.value,
        'password': password.value,
        'create': true
    }
    var request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log("trying to send account info...")
        }
    };
    request.open("POST", "/account");
    request.send(JSON.stringify(data));
    // request.onload = function () {
    //     createDiv = document.getElementById('create');
    //     console.log("response received")
    //     if (request.status == 200) {
    //         createDiv.innerHTML = '<br /><h2 style="color:green"><i>Account ' + data['username'] + ' created successfully</i></h2>'
    //     } else {
    //         createDiv.innerHTML = '<br /><h2 style="color:red"><i>' + request.responseText + '</i></h2>'
    //     }
    // }
    // Clear the form inputs
    username.value = "";
    password.value = "";
}

function loginUser() {
    const username = document.getElementById("login-username");
    const password = document.getElementById("login-password");

    data = {
        'username': username.value,
        'password': password.value,
        'create': false
    }
    var request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log("trying to send account info...")
        }
    };
    request.open("POST", "/account");
    request.send(JSON.stringify(data));
    request.onload = function () {
        loginDiv = document.getElementById('login');
        if (request.status == 200) {
            loginDiv.innerHTML = '<br /><h2 style="color:green"><i>Login successful; Welcome ' + data['username'] + '</i></h2>'
        } else {
            loginDiv.innerHTML = '<br /><h2 style="color:red"><i>' + request.responseText + '</i></h2>'
        }
    }
    username.value = "";
    password.value = "";
}

