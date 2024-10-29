document.addEventListener('DOMContentLoaded', function () {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file');
    const tableHead = document.getElementById('table-head');
    const tableBody = document.getElementById('table-body');
    const simulateBtn = document.getElementById('simulate-btn');
    const simulationResults = document.getElementById('simulation-results');

    let dataTable;

    // Handle file upload form submission
    uploadForm.addEventListener('submit', function (e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                populateTable(data);
                simulateBtn.style.display = 'block';  // Show simulate button
            }
        })
        .catch(err => {
            console.error('Error uploading file:', err);
            alert('An error occurred while uploading the file.');
        });
    });

    // Handle simulation button click
    simulateBtn.addEventListener('click', function () {
        fetch('/simulate', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            displaySimulationResults(data);
        })
        .catch(err => {
            console.error('Error during simulation:', err);
            alert('An error occurred during the simulation.');
        });
    });

    // Function to display uploaded data in DataTable
    function populateTable(data) {
        // Clear existing table data if needed
        tableHead.innerHTML = '';
        tableBody.innerHTML = '';

        if (data.length > 0) {
            // Create table header
            let headerHTML = '<tr>';
            Object.keys(data[0]).forEach(key => {
                headerHTML += `<th>${key}</th>`;
            });
            headerHTML += '</tr>';
            tableHead.innerHTML = headerHTML;

            // Create table rows
            data.forEach(row => {
                let rowHTML = '<tr>';
                Object.values(row).forEach(value => {
                    rowHTML += `<td>${value}</td>`;
                });
                rowHTML += '</tr>';
                tableBody.innerHTML += rowHTML;
            });

            // Initialize DataTable
            if (dataTable) {
                dataTable.destroy();  // Destroy existing DataTable instance if it exists
            }
            dataTable = $('#data-table').DataTable();  // Initialize new DataTable
        }
    }

    // Function to display simulation results
    function displaySimulationResults(data) {
        let resultsHTML = '<table>';
        resultsHTML += '<tr><th>Random Data</th><th>Acceptance Status</th></tr>';
        for (let i = 0; i < data.random_data.length; i++) {
            resultsHTML += `<tr><td>${data.random_data[i]}</td><td>${data.acceptance_results[i]}</td></tr>`;
        }
        resultsHTML += '</table>';
        simulationResults.innerHTML = resultsHTML;
    }
});
