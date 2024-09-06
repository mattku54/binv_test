            // Convert element of date time class to more readable string
            document.querySelectorAll('.date-time').forEach(function(element) {
                
                // Get the string
                let date_time = element.textContent;
                console.log(`Date-time: ${date_time}`);
                
                // Convert to ISO format
                let date_obj = new Date(date_time.replace(' ', 'T') + 'Z');
                console.log(`date_obj: ${date_obj}`);
    
                // Convert to PST and correct format
                let dt_options = {timeZone:'America/Los_Angeles',
                    year:'numeric',
                    month:'short',
                    day:'numeric',
                    hour:'2-digit',
                    minute:'2-digit',
                    hour12:'true'
                }
                let form_dt = new Date(date_obj).toLocaleString("en-US", dt_options);
                console.log(`form_dt: ${form_dt}`);
    
                // Change the content to formmated date time
                element.textContent = form_dt;
            });