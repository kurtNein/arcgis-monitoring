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
async function fetchData(url) {
    try {
        // Set to "Loading..." state
        updateOutput('alert info', 'Loading...', 'output');
        updateOutput('', '', 'response')

        // Wait for the fetch request to complete
        let response = await fetch(url);
        let data = await response.json();
        const formattedData = formatDictAsHTML(data.message);
        // Get the count of key-value pairs in the dictionary
        const count = Object.keys(data.message).length;
        // Set to "Success" state
        updateOutput('main content', formattedData, 'response');
        updateOutput('alert success', `Success - ${count} records found.`, 'output');
    } catch (error) {
        // Set to "Error" state
        updateOutput('alert error', 'Error fetching data.', 'output');
    }
}

// Async function for "Get List Count" button
document.getElementById('fetch-list').addEventListener('click', async function() {
    await fetchData('/api/data', 'output');
});

// Async function for "Get User Info" button
document.getElementById('fetch-user').addEventListener('click', async function() {
    await fetchData('/api/user', 'output');
});

// Async function for "Get Status" button
document.getElementById('fetch-status').addEventListener('click', async function() {
    await fetchData('/api/status', 'output');
});
