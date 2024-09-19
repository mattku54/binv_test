// Client side validation for email

document.addEventListener("DOMContentLoaded", function() {
    document.querySelector('#register').addEventListener("submit", function(event) {

        // Make sure all form elements are filled in
        const form_elements = document.querySelector('#register').elements;

        for (let i=0; i < form_elements.length - 1; i++) {
            if (form_elements[i].value === "") {
                event.preventDefault();
                alert("Please fill in every entry on the form")
            }
        }

        // Make sure a pasadena.edu or go.pasadena.edu email is used
        const email = document.querySelector('#email').value;
        const emailPattern = /^[^\s@]+@pasadena\.edu$/;
        const emailPattern2 = /^[^\s@]+@go.pasadena\.edu$/;
        
        if (!emailPattern.test(email) && !emailPattern2.test(email)) {
            event.preventDefault();
            alert("Please enter a valid go.pasadena.edu or pasadena.edu email address.")
        }

        // Make sure password and confirmation match    
        const password = document.querySelector('#password').value;
        const confirmation = document.querySelector('#confirmation').value;

        if (password != confirmation) {
            event.preventDefault();
            alert("Password and Confirmation do not match")
            return false
        }

    }
    )
});