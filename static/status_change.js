// This script should change the color of a 'status' cell based on what its status is

        // Loop through every cell of class status
        let cells = document.getElementsByClassName("status")

        n = cells.length;

        for (let i = 0; i < n; i++) {
            // Set the cell as one piece of cell data
            let cell = cells[i]

            // Get the value of the item
            var value = cell.innerText;

            // Set the background color of the cell depending on value
            if (value == 'clean')
                {
                    cell.style.backgroundColor = 'rgba(38, 194, 129, 0.5)';
                }
            else if (value == 'missing')
                {
                    cell.style.backgroundColor = 'rgba(255,0,0,0.8)';
                }
            else if (value == 'partial')
                {
                    cell.style.backgroundColor = 'rgba(249, 180, 45, 0.5)';
                }
            else if (value == 'dirty')
                {
                    cell.style.backgroundColor = 'rgba(227, 186, 143, 1)';
                }
        }
