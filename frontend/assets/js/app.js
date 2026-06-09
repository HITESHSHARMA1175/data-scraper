let API_URL = '/api';
if (window.location.hostname === 'localhost' && window.location.port !== '5000') {
    API_URL = 'http://localhost:5000/api';
}

        // Toggle input method
        function toggleInputMethod() {
            const method = document.querySelector('input[name="inputMethod"]:checked').value;
            const urlGroup = document.getElementById('urlInputGroup');
            const cityKeywordGroup = document.getElementById('cityKeywordInputGroup');
            
            if (method === 'url') {
                urlGroup.classList.remove('hidden');
                cityKeywordGroup.classList.add('hidden');
            } else {
                urlGroup.classList.add('hidden');
                cityKeywordGroup.classList.remove('hidden');
            }
        }

        // Start scraping
        async function startScraping() {
            const method = document.querySelector('input[name="inputMethod"]:checked').value;
            let payload = {};

            if (method === 'url') {
                const urlInput = document.getElementById('urlInput');
                const url = urlInput.value.trim();
                if (!url) {
                    showMessage('Please enter a URL', 'error');
                    return;
                }
                payload = { url };
            } else {
                const city = document.getElementById('cityInput').value.trim();
                const keyword = document.getElementById('keywordInput').value.trim();
                if (!city || !keyword) {
                    showMessage('Please enter both City and Keyword', 'error');
                    return;
                }
                payload = { city, keyword };
            }

            const scrapeBtn = document.getElementById('scrapeBtn');
            const message = document.getElementById('scrapeMessage');
            const loading = document.getElementById('scrapeLoading');

            scrapeBtn.disabled = true;
            loading.style.display = 'block';
            message.style.display = 'none';

            try {
                const response = await fetch(`${API_URL}/scrape`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                const contentType = response.headers.get("content-type");
                if (contentType && contentType.indexOf("application/json") !== -1) {
                    const result = await response.json();

                    if (result.success) {
                        showMessage('Scraping completed successfully!', 'success');
                        displayPreview(result.data, result.filename);
                        refreshFiles();
                        refreshStats();
                        // Clear inputs based on chosen method
                        if (method === 'url') {
                            const urlInput = document.getElementById('urlInput');
                            if (urlInput) urlInput.value = '';
                        } else {
                            const cityInput = document.getElementById('cityInput');
                            const keywordInput = document.getElementById('keywordInput');
                            if (cityInput) cityInput.value = '';
                            if (keywordInput) keywordInput.value = '';
                        }
                    } else {
                        showMessage(`Error: ${result.error}`, 'error');
                    }
                } else {
                    const text = await response.text();
                    showMessage(`Server Error (Timeout/Crash). Check backend logs.`, 'error');
                }
            } catch (error) {
                showMessage(`Error: ${error.message}`, 'error');
            } finally {
                scrapeBtn.disabled = false;
                loading.style.display = 'none';
            }
        }

        // Display preview
        function displayPreview(data, filename) {
            const preview = document.getElementById('previewContent');
            
            if (!data || data.length === 0) {
                preview.innerHTML = '<p>No data to display</p>';
                return;
            }

            let html = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 style="color: #333; margin: 0;">Results from ${filename}</h3>
                    <button onclick="downloadFile('${filename}')" style="padding: 5px 15px;">Download CSV</button>
                </div>
                <p style="color: #666; margin-bottom: 15px;">Records found: <strong>${data.length}</strong></p>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Address</th>
                                <th>Phone</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            data.slice(0, 20).forEach(row => {
                html += `
                    <tr>
                        <td>${escapeHtml(row.Name || '')}</td>
                        <td>${escapeHtml(row.Address || '')}</td>
                        <td>${escapeHtml(row.Phone || 'N/A')}</td>
                    </tr>
                `;
            });

            html += `
                        </tbody>
                    </table>
                </div>
                ${data.length > 20 ? `<p style="color: #666;">Showing 20 of ${data.length} records. Download the file to see all.</p>` : ''}
            `;

            preview.innerHTML = html;
        }

        // Refresh files list
        async function refreshFiles() {
            try {
                const response = await fetch(`${API_URL}/files`);
                const result = await response.json();

                if (result.success) {
                    const filesList = document.getElementById('filesList');
                    
                    if (result.files.length === 0) {
                        filesList.innerHTML = '<p>No files found</p>';
                        return;
                    }

                    let html = '<div class="files-list">';
                    result.files.forEach(file => {
                        const date = new Date(file.modified).toLocaleString();
                        const sizeKB = (file.size / 1024).toFixed(2);
                        html += `
                            <div class="file-item" onclick="viewFile('${file.name}')" style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div class="file-name">📄 ${file.name}</div>
                                    <div class="file-info">
                                        Size: ${sizeKB} KB | Modified: ${date}
                                    </div>
                                </div>
                                <button onclick="downloadFile('${file.name}', event)" style="padding: 5px 10px; font-size: 14px; cursor: pointer; border: 1px solid #4a6ee0; background: transparent; color: #4a6ee0; border-radius: 4px;">Download</button>
                            </div>
                        `;
                    });
                    html += '</div>';
                    filesList.innerHTML = html;
                }
            } catch (error) {
                console.error('Error fetching files:', error);
            }
        }

        // Download file
        function downloadFile(filename, event) {
            if (event) {
                event.stopPropagation();
            }
            window.location.href = `${API_URL}/download/${encodeURIComponent(filename)}`;
        }

        // View file
        async function viewFile(filename) {
            try {
                const response = await fetch(`${API_URL}/file/${encodeURIComponent(filename)}`);
                const result = await response.json();

                if (result.success) {
                    displayPreview(result.data, result.filename);
                    switchTab('preview');
                }
            } catch (error) {
                console.error('Error viewing file:', error);
            }
        }

        // Refresh statistics
        async function refreshStats() {
            try {
                const response = await fetch(`${API_URL}/stats`);
                const result = await response.json();

                if (result.success) {
                    document.getElementById('totalFiles').textContent = result.total_files;
                    document.getElementById('totalRecords').textContent = result.total_records;
                }
            } catch (error) {
                console.error('Error fetching stats:', error);
            }
        }

        // Switch tabs
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });

            // Show selected tab
            const tabEl = document.getElementById(tabName);
            if (tabEl) tabEl.classList.add('active');

            // Activate corresponding button using data-tab attribute
            const btn = document.querySelector(`.tab-button[data-tab="${tabName}"]`);
            if (btn) btn.classList.add('active');

            if (tabName === 'files') {
                refreshFiles();
            }
        }

        // Show message
        function showMessage(text, type) {
            const message = document.getElementById('scrapeMessage');
            message.textContent = text;
            message.className = `message ${type}`;
            message.style.display = 'block';

            if (type !== 'error') {
                setTimeout(() => {
                    message.style.display = 'none';
                }, 5000);
            }
        }

        // Escape HTML
        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        // Initialize on load
        window.addEventListener('load', () => {
            refreshStats();
            refreshFiles();
        });
