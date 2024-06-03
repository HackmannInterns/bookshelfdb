// ==UserScript==
// @name         isbn sender
// @namespace    https://barcodescanr.com/
// @version      1.0
// @description  Checks the content of #scan-result-text and prints it if it is numeric
// @author       Your Name
// @match        *://*/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    let code = 0;

    //     function sendPostRequest(url, text) {
    //       fetch(url, {
    //         method: "POST",
    //         body: '"id": "' + text + '"',
    //         headers: {
    //           "Content-type": "application/json; charset=UTF-8"
    //         }
    //       })
    //     .then(response => {
    //         if (!response.ok) {
    //             throw new Error('Network response was not ok');
    //         }
    //         return response.json();
    //     })
    //     .then(data => {
    //         console.log('Success:', data);
    //     })
    //     .catch((error) => {
    //         console.error('Error:', error.message);
    //     });
    // }

    // Function to check if the content is numeric
    function isNumeric(value) {
        return /^-?\d+$/.test(value);
    }

    // Function to check and print the content of the element
    function checkAndPrintContent() {
        const element = document.getElementById('scan-result-text');
        if (element) {
            const content = element.textContent.trim();
            if (isNumeric(content) && content != code) {
                code = content;
                console.log(content);
                window.open("http://192.168.0.36:5000/?isbn=" + content, "_blank");
                // sendPostRequest("https://httpbin.org/post", content)
                // sendPostRequest("http://127.0.0.1:5000/post", content)
            } else {
              // Non numberic
            }
        } else {
          //not found
        }
    }

    // Check the content immediately and also set an interval to check periodically
        // Define a callback function to handle the JSONP response
    window.handleJsonpData = function(data) {
        console.log('Received data:', data);
        // Process the data as needed
    };
    checkAndPrintContent();
    setInterval(checkAndPrintContent, 1000); // Check every second
})();
