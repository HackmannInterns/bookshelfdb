// ==UserScript==
// @name         isbn sender
// @namespace    https://github.com/HackmannInterns/bookshelfdb
// @version      1.0
// @description  Checks the content of #scan-result-text and prints it if it is numeric
// @author       Hackmann Interns
// @match        *://scanapp.org/*
// @grant        none
// ==/UserScript==

var instance = "http://localhost:5000";

(function() {
    'use strict';
    let code = 0;

    // Function to check if the content is numeric
    function isNumeric(value) {
        return /^-?\d+$/.test(value);
    }

    // Function to check and send the content of the element
    function checkAndSendContent() {
        const element = document.getElementById('scan-result-text');
        if (element) {
            const content = element.textContent.trim();
            if (isNumeric(content) && content != code) {
                code = content;
                console.log(content);
                window.open(instance + "/add-book?isbn=" + content, "_blank");
            } else {
              // Non numberic
            }
        } else {
          //not found
        }
    }

    checkAndSendContent();
    setInterval(checkAndSendContent, 1000); // Check every second
})();
