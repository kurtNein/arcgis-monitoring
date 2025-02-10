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
async function fetchData(url, id_output, id_response, output_message) {
    try {
        // Set to "Loading..." state
        updateOutput('alert info', 'Loading...', id_output);
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


async function yourFunction(){

    let now = new Date();
    let hours = formatTime(now.getHours());
    let minutes = formatTime(now.getMinutes());
    let seconds = formatTime(now.getSeconds());

    await fetchData('/api/dashboard', 'output2', 'response2', 'Status of last EGDB backup');
    await fetchData('/api/status', 'output3', 'response3', `Status of web adaptors as of ${hours}:${minutes}:${seconds}`);
    await fetchData('/api/last_stats', 'output4', 'response4', 'Details of last EGDB backup');
    await fetchData('/api/sde_users', 'output5', 'response5', 'Current users in .sde');

    setTimeout(yourFunction, 15_000);
}

yourFunction();

// Async function for "Last Backup" button
document.getElementById('last-backup2').addEventListener('click', async function() {
    await fetchData('/api/last_stats', 'output2', 'response2', 'Details of last EGDB backup');
});
