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
async function fetchData(url, id) {
    try {
        // Set to "Loading..." state
        updateOutput('alert info', 'Loading...', id);
        updateOutput('', '', 'response2')

        // Wait for the fetch request to complete
        let response = await fetch(url);
        let data = await response.json();
        const formattedData = formatDictAsHTML(data.message);
        // Get the count of key-value pairs in the dictionary
        const count = Object.keys(data.message).length;
        // Set to "Success" state
        updateOutput('main content', formattedData, 'response2');
        updateOutput('alert success', `Success - ${count} items.`, 'output2');
    } catch (error) {
        // Set to "Error" state
        updateOutput('alert error', 'Error fetching data.', 'output2');
    }
}

fetchData('/api/dashboard', 'response2')


// Async function for "Last Backup" button
document.getElementById('last-backup2').addEventListener('click', async function() {
    await fetchData('/api/last_stats', 'output2');
});
