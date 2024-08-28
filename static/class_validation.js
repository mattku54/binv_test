        // Validate the form elements that include a semester
        document.addEventListener('DOMContentLoaded', function() {
            
            document.querySelector('#class').addEventListener("submit", function(event) {

                // Make sure form elements are all filled in
                const elements = document.querySelector('#class').elements;

                for (let i = 0; i < elements.length - 1; i++) {
                    
                    if (elements[i].value === "") {
                        event.preventDefault();
                        alert("Please fill out all form elements");
                    }
                }

                // Make sure semester is in correct form
                let sem_pat = ["FA", "WI", "SP", "SU"];
                let semester = document.querySelector('#semester').value;

                let sem_part = semester.slice(0 , 2);
                let yr_part = semester.slice(2);

                if (sem_pat.includes(sem_part) && /^\d{2}$/.test(yr_part)) {
                    console.log("Semester: {semester} valid")
                }
                else {
                    event.preventDefault();
                    alert("Invalid semester format")
                    alert("Semester must be FA, WI, SP, SUM followed by 2 digit year")
                }
            })

        }) 