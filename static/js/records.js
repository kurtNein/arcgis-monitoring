// Helper function to update the class and text of the output element
function updateOutput(className, text, id) {
    const outputElement = document.getElementById(id);
    outputElement.className = `output ${className}`;
    outputElement.innerHTML = text;
}

function formatDictAsHTML(dict) {
    const lines = Object.entries(dict).map(([key, value]) => {
        return `<div><strong>${key}:</strong> ${value}</div>`;
    });
    return lines.join('');
}

// Async function to fetch data
async function fetchData(url, id_output, id_response, output_message, loading_message) {
    try {
        // Set to "Loading..." state
        updateOutput('alert info', loading_message, id_output);
        updateOutput('', '', id_response)

        // Wait for the fetch request to complete
        let response = await fetch(url);
        let data = await response.json();
        const formattedData = formatDictAsHTML(data.message);
        // Get the count of key-value pairs in the dictionary
        const count = Object.keys(data.message).length;
        // Set to "Success" state
        updateOutput('main content', formattedData, id_response);
        updateOutput('alert success', `${output_message} - ${count} items.`, id_output);
    } catch (error) {
        // Set to "Error" state
        updateOutput('alert error', 'Error fetching data.', id_output);
    }
}

function formatTime(number) {
    return number < 10 ? '0' + number : number;
}

fetchData('/api/dashboard', 'output2', 'response2', 'Status of last EGDB backup', 'Fetching last EGDB details...');
fetchData('/api/sde_users', 'output5', 'response5', 'Current users in .sde', 'Counting directly connected users on EGDB...');
fetchData('/api/last_stats', 'output4', 'response4', 'Details of last EGDB backup', 'Fetching feature layers of last EGDB backup...');
    
async function yourFunction(){

    let now = new Date();
    let hours = formatTime(now.getHours());
    let minutes = formatTime(now.getMinutes());
    let seconds = formatTime(now.getSeconds());

    await fetchData('/api/status', 'output3', 'response3', `Status of web adaptors as of ${hours}:${minutes}:${seconds}`, 'Getting http response codes...');
    
    setTimeout(yourFunction, 10_000);
}

yourFunction();
