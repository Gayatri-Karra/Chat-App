// Get the current URL
var urlPath = window.location.pathname;

var wsURL = "ws://127.0.0.1:8001" + urlPath;

const chatData = 'Hello, server!';


let socket;
let connectAttempts = 0;
let time = 1000;

function connectWebSocket(){

    socket = new WebSocket(wsURL);
    
    socket.addEventListener('open', (event) => {
        console.log("webSocket connection opened:", event);
        connectAttempts = 0;
        time = 1000;
    });
    
    socket.addEventListener('error', (event) => {
        console.log("webSocket connection error: ", event);
    });
    
    
    socket.addEventListener('close', (event) => {
        console.log("webSocket connection closed: ", event);
        connectAttempts++;
        time += 1000;
        if (connectAttempts < 15){
            setTimeout(() => {
                connectWebSocket();
            }, time);

        }
    });
    
    
    
    // Event listener for when a message is received
    socket.addEventListener('message', (event) => {
        const receivedMessage = JSON.parse(event.data);
        addChatObject(receivedMessage);
    });
}

connectWebSocket();

const send_button = document.getElementById("send-button");
const message_box = document.getElementById("message-box");

const message_form = document.getElementById("message-form");

message_form.addEventListener('submit', function(event) {
    event.preventDefault();

    var user_message = message_box.value;
    message_box.value = '';
    if (user_message == ''){
        return false;
    }
    encryptMessage(user_message, sharedKey).then(encrypted_message => {
        

        var csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

        
        fetch(urlPath, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFTOKEN': csrfToken,
            },
            body : JSON.stringify({message: encrypted_message})
        })

        .then(response => {
            return response.json()
        })

        .then(data => {
            socket.send(JSON.stringify(data));
            addChatObject(data)
        })
        .catch(error =>{
            console.log("Error: ", error);
        })
    })

})


function addChatObject(chatData){
    const messageContainer = document.getElementById('messageContainer');

    var direction = "flex-row"
    if(chatData.created_by === user){
        direction = "flex-row-reverse"
    }
    // var messageData = JSON.parse(chatData.message);
    chatData.message = chatData.message.replace(/'/g, '"');
    var messageObject = JSON.parse(chatData.message);

    const ivArray = new Uint8Array(Object.keys(messageObject.iv).map(key => messageObject.iv[key]));

    // Convert data object to Uint8Array
    const dataArray = new Uint8Array(Object.keys(messageObject.data).map(key => messageObject.data[key]));

    var encrypted_message = { iv: ivArray, data: dataArray }

    decryptMessage(encrypted_message, sharedKey).then(decrypted_message => {
        messageContainer.innerHTML += `
        <div class="flex ${direction} py-2">
            <div class="p-2 bg-gray-100 rounded-lg">
                <p class="text-lg">${decrypted_message}</p>
                <p class="text-sm text-gray-600">${ chatData.created_by } | ${ chatData.created_at }</p>
            </div>
        </div>
    `

        messageContainer.scrollTop = messageContainer.scrollHeight;
    }).catch(error => {
        console.error('Decryption error:', error);
    });
                   
}


function load_messages(){

    const currentUrl = window.location.href;
    var urlPath = window.location.pathname

    fetch(`/api${urlPath}`)
    .then(response => {
        if (!response.ok) {
            throw new Error(response);
        }
        return response.json();
    })
    .then(data => {
        // Handle the response data containing the messages
        for(i = 0; i < data.messages.length; i++){
            addChatObject(data.messages[i]);
        }
        // Process the messages here
    })
    .catch(error => {
        console.error('Error fetching messages:', error);
        // Handle error
    });
}

load_messages();