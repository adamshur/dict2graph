document.addEventListener('DOMContentLoaded', () => {
    const wordInput = document.getElementById('word');
    const maxNodesInput = document.getElementById('max-nodes');
    const depthInput = document.getElementById('depth');
    const neighborLimitInput = document.getElementById('neighbor-limit');
    const outgoingCheckbox = document.getElementById('outgoing');
    const incomingCheckbox = document.getElementById('incoming');
    const visualizeBtn = document.getElementById('visualize-btn');
    const networkContainer = document.getElementById('network-container');
    const loading = document.getElementById('loading');

    let network = null;

    function validateDirections() {
        if (!outgoingCheckbox.checked && !incomingCheckbox.checked) {
            alert('Please select at least one relationship direction');
            return false;
        }
        return true;
    }

    async function visualizeWord() {
        const word = wordInput.value.trim();
        if (!word) {
            alert('Please enter a word');
            return;
        }

        if (!validateDirections()) {
            return;
        }

        // Show loading state
        loading.style.display = 'block';
        visualizeBtn.disabled = true;
        
        // Reset progress
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        progressFill.style.width = '0%';
        progressText.textContent = 'Generating visualization...';

        // Set up SSE for progress updates
        const eventSource = new EventSource(`/progress/${word}`);
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            progressFill.style.width = `${data.progress}%`;
            progressText.textContent = data.message;
        };

        eventSource.onerror = () => {
            eventSource.close();
        };

        try {
            const response = await fetch('/visualize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    word: word,
                    max_nodes: parseInt(maxNodesInput.value),
                    depth: parseInt(depthInput.value),
                    neighbor_limit: parseInt(neighborLimitInput.value),
                    directions: {
                        outgoing: outgoingCheckbox.checked,
                        incoming: incomingCheckbox.checked
                    }
                })
            });

            const data = await response.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            // Destroy previous network if it exists
            if (network) {
                network.destroy();
            }

            // Create new network
            const container = document.getElementById('network-container');
            network = new vis.Network(
                container,
                data.graph_data,
                data.graph_data.options
            );

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while generating the visualization');
        } finally {
            loading.style.display = 'none';
            visualizeBtn.disabled = false;
        }
    }

    // Event listeners
    visualizeBtn.addEventListener('click', visualizeWord);
    
    // Allow Enter key to trigger visualization
    wordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            visualizeWord();
        }
    });

    // Input validation
    function validateNumberInput(input, min, max) {
        input.addEventListener('change', () => {
            const value = parseInt(input.value);
            if (value < min) input.value = min;
            if (value > max) input.value = max;
        });
    }

    validateNumberInput(maxNodesInput, 10, 200);
    validateNumberInput(depthInput, 1, 4);
    validateNumberInput(neighborLimitInput, 1, 20);
});