document.addEventListener('DOMContentLoaded', (event) => {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const progressBar = document.querySelector('.progress');
    const status = document.getElementById('status');
    const result = document.getElementById('result');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            status.textContent = 'Uploading and processing...';
            progressBar.style.width = '0%';

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    progressBar.style.width = percentCompleted + '%';
                }
            });

            const data = await response.json();

            if (data.success) {
                status.textContent = 'Processing complete!';
                result.innerHTML = `<p>Output video: ${data.output}</p>`;
            } else {
                status.textContent = 'Error: ' + data.error;
            }
        } catch (error) {
            console.error('Error:', error);
            status.textContent = 'An error occurred during upload or processing.';
        }
    });
});