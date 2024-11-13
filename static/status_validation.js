// Validate that student has updated status of all items in the bin

document.addEventListener('DOMContentLoaded', () => {
    console.log ('DOM Content loaded')

    // Find the event form
    document.querySelector('#event_form').addEventListener('submit', (event) => {

        // Make sure a status has been filled in for every item
        const form_elements = event.target.elements;

        // Check all form elements
        for (let i=0; i < form_elements.length; i++) {

            console.log(`Checking: ${form_elements[i].name} Value: ${form_elements[i].value}`)

            if (form_elements[i].tagName === "SELECT"){
                
                if (form_elements[i].selectedIndex === 0 || form_elements[i].value === "") {
                    // Prevent submission if any statusses are not marked
                    event.preventDefault();
                    alert("Please select a status for every item before submitting")
                    console.log(`${form_elements[i].name} not marked`)
                    break
                }

            }
   
        }
    })
})

