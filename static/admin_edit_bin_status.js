document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM Loaded");

    document.querySelector('#first_button').addEventListener('click', function(event) {
        // Prevent the default (which is form submission)
        event.preventDefault();

        console.log(`First button form submission prevented`)

        // Confirm bin will send an ajax request to confim the bin and then unhide the rest of the form
        confirm_bin()
    })
    
})

function confirm_bin() {

    // Use an ajax request to confirm that the bin exists before user can update the rest of the bins
    let room_num = document.getElementById('room_num')
    let bin_num  = document.getElementById('bin_num')

    console.log(`Confim_bin - room_num: ${room_num.value} bin_num: ${bin_num.value}`)

    if (room_num.value == '' || bin_num.value == '') {
        alert("Please input a valid room number and bin number")
        return
    }
    else {
        // Initialize new ajax request
        var aj = new XMLHttpRequest();

        console.log(`Ajax initialized`)

        // Create the ajax function
        aj.onreadystatechange = function() {
            if (aj.readyState == 4 && aj.status == 200){

            console.log(`Ajax is ready`)

                // Parse through the data, the data will either be false or the bin number
                var data = JSON.parse(aj.responseText)
                
                // Response text should be true if bin is found and false if not
                if (data === 'false') {
                    alert("Bin not found, please select a valid room number and bin number")
                    return
                }
                else{

                    console.log(`Bin number found: ${data}`)
                    // Update header instructions
                    var header = document.getElementById('header')
                    header.textContent = 'Update status of items in bin number ' + data

                    // Unhide the next inputs
                    unhide_inputs()
                    return
                }
            }
            else{
                console.log(`AJ Readystate: " + ${aj.readyState} + "Status: " + ${aj.status}`);
                return
            }
        }
        // Gather the data from the ajax request
        console.log(`AJAX Opened: Room-num: ${room_num.value} bin_num: ${bin_num.value}`);
        aj.open("GET", '/confirm_bin?room_num=' + encodeURIComponent(room_num.value) + '&bin_num= ' + encodeURIComponent(bin_num.value), true);
        aj.send()

    }
}

function unhide_inputs() {
    
    // Unhide the inputs for the bin_contents and statusses and input2 button
    var hidden_rows = document.getElementsByClassName('input2')
    
    for (var i = 0; i < hidden_rows.length; i++){

        hidden_rows[i].style.display = "block";

    }

    // Hide the first selections
    var unhidden_rows = document.getElementsByClassName('input1')

    for (var i = 0; i < unhidden_rows.length; i++){

        unhidden_rows[i].style.display = "none";

    }
}