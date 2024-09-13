const API_BASE_URL = 'http://localhost:5000/api';

let folderList = [];
let recordList = [];

document.addEventListener('DOMContentLoaded', function() {
    const nav = document.querySelector('nav');
    const main = document.querySelector('main');
    const menuIcon = document.querySelector('.menu-icon');
    const setsIcon = document.querySelector('.sets-icon');
    const mainFuncContainer = document.querySelector('.main-func');
    const refreshBtn = document.getElementById('refreshBtn');
    const folderContainer = document.getElementById('folderContainer');
    const createFolderBtn = document.getElementById('createFolderBtn');
    const deleteBtn = document.getElementById('deleteBtn');
    const fileInput = document.getElementById('fileInput');
    const settingsDialog = document.getElementById('settingsDialog');
    const settingsContent = document.getElementById('settingsContent');
    const closeBackendBtn = document.getElementById('closeBackendBtn');
    const settingsCloseBtn = document.getElementById('settingsCloseBtn');
    const snackbar = document.getElementById("snackbar");
    let deleteMode = false;
    
    refreshBtn.addEventListener('click', fetchFolders);
    fileInput.addEventListener('change', handleFileUpload);
    createFolderBtn.addEventListener('click', handleFolderUpload);
    deleteBtn.addEventListener('click', toggleDeleteMode);
    closeBackendBtn.addEventListener('click', closeBackend);
    
    menuIcon.addEventListener('click', function() {
        nav.style.display = nav.style.display === 'none' ? 'flex' : 'none';
        main.style.width = main.style.width === '100%' ? 'calc(100% - 200px)' : '100%';
    });
    setsIcon.addEventListener('click', function() {
        settingsDialog.showModal();
    });

    settingsCloseBtn.addEventListener('click', () => {
        settingsDialog.close();
    });
    settingsDialog.addEventListener('click', (event) => {
        if (!settingsContent.contains(event.target)) {
            settingsDialog.close();
        }
    });

    folderContainer.addEventListener('dragstart', (e) => {
        if (e.target.draggable) {
            const folderName = e.target.closest('.folder').querySelector('.folder-header span').textContent;
            const fileName = e.target.innerHTML;
            e.dataTransfer.setData('text/plain', e.target.outerHTML);
            e.dataTransfer.setData('folderName', folderName);
            e.dataTransfer.setData('fileName', fileName);
            e.dataTransfer.effectAllowed = 'move';
            setTimeout(() => {
                e.target.style.display = 'none';
            }, 0);
        }
    });
    folderContainer.addEventListener('dragend', (e) => {
        if (e.target.draggable) {
            e.target.style.display = '';
            if (!e.dataTransfer.dropEffect || e.dataTransfer.dropEffect === 'none') {
                e.target.style.display = '';
            }
        }
    });
    folderContainer.addEventListener('click', (e) => {
        const target = e.target.closest('.folder, .file-link');
        if (target) {
            if (target.matches('.folder')) {
                if (deleteMode && confirm('確定要刪除整個資料夾嗎?')) {
                    const folderName = target.querySelector('.folder-header span').textContent;
                    deleteFolder(folderName);
                    target.remove();
                }
            } else if (target.matches('.file-link')) {
                const folderName = target.closest('.folder').querySelector('.folder-header span').textContent;
                const fileName = target.innerHTML;
                if (deleteMode) {
                    deleteFile(folderName, fileName);
                    target.remove();
                } else {
                    window.open(`${API_BASE_URL}/pdf/${folderName}/${fileName}`, '_blank');
                }
            }
        }
    });

    fetchFolders();
    fetchRecords();
  
    function dragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }
  
    function dragLeave(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
    }
  
    function drop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        const targetFolderContent = e.currentTarget.querySelector('.folder-content');
        const targetFolder = targetFolderContent.parentNode.querySelector('.folder-header span').textContent;
        const dt = e.dataTransfer;
          
        // 文件拖放的情況
        const files = dt.files;
        if (files.length > 0) {
            handleFileAddition(targetFolderContent, files);
            return;
        }
          
        // HTML 元素拖放的情況
        const data = dt.getData('text');
        const folderName = dt.getData('folderName')
        const fileName = dt.getData('fileName');
        const draggedElement = document.createElement('div');
        draggedElement.innerHTML = data;
        const newElement = draggedElement.firstChild;
    
        if (targetFolder === folderName) {
            const originalElement = document.querySelector(`[draggable="true"][style="display: none;"]`);
            if (originalElement) {
                originalElement.style.display = '';  // 取消隱藏，使其重新顯示
            }
            return;
        }

        if (getTargetFile(targetFolderContent, fileName)) {
            if (confirm(`資料夾 "${targetFolder}" 已有一個名為 "${fileName}" 的檔案，是否確定要覆蓋？`)) {
                if (dt.effectAllowed === 'move') {
                    const originalElement = document.querySelector(`[draggable="true"][style="display: none;"]`);
                    if (originalElement) {
                        originalElement.remove();
                    }
                }
            } else {
                const originalElement = document.querySelector(`[draggable="true"][style="display: none;"]`);
                if (originalElement) {
                    originalElement.style.display = '';  // 取消隱藏，使其重新顯示
                }
                return;
            }
        } else {
            if (dt.effectAllowed === 'move') {
                const originalElement = document.querySelector(`[draggable="true"][style="display: none;"]`);
                if (originalElement) {
                    originalElement.remove();
                }
            }
        
            targetFolderContent.appendChild(newElement);
        }
        
        moveFile(fileName, folderName, targetFolder);
    }

    function handleFileUpload(e) {
        const files = e.target.files;
        const targetFolderName = fileInput.getAttribute('data-target-folder');
        const targetFolder = getTargetFolder(targetFolderName);

        if (targetFolder) {
            const folderContent = targetFolder.querySelector('.folder-content');
            handleFileAddition(folderContent, files);
        }

        // 清除文件輸入，允許重複上傳相同文件
        fileInput.value = '';
    }

    function handleFolderUpload(e) {
        const folderName = prompt('請輸入文件夾名稱：');
        if (isValidFolderName(folderName)) {
            alert('請輸入有效的資料夾名稱。名稱中不得包含 \ / : * ? " < > | 等非法字元，也不得為空白。');
        } else if (getTargetFolder(folderName)) {
            alert('資料夾名稱不可重複，請輸入一個新的名稱。');
        } else {
            createFolder(folderName);
            uploadFolder(folderName);
        }
    }

    function toggleDeleteMode() {
        deleteMode = !deleteMode;
        if (deleteMode) {
            deleteBtn.style.backgroundColor = '#d32f2f';
            deleteBtn.classList.add('fullWidth');
            createFolderBtn.style.display = 'none';
        } else {
            deleteBtn.style.backgroundColor = '#f44336';
            deleteBtn.classList.remove('fullWidth');
            createFolderBtn.style.display = 'block';
        }
        folderContainer.style.cursor = deleteMode ? 'not-allowed' : 'default';
    }

    function isValidFolderName(folderName) {
        const invalidChars = /[\\/:*?"<>|]/;
        // 檢查字串是否包含非法字元，且不可以是空白字串或僅包含空格
        return (invalidChars.test(folderName) || folderName.trim() === '');
    }
    
    function getTargetFolder(targetFolderName) {
        return Array.from(folderContainer.children).find(
            folder => folder.querySelector('.folder-header span').textContent === targetFolderName
        );
    }
    
    function getTargetFile(folderContent, targetFileName) {
        return Array.from(folderContent.children).find(
            file => file.innerHTML === targetFileName
        );
    }

    function toggleFolder(e) {
        if (e.target.classList.contains('upload-btn')) return;
        // 獲取最近的 folder-header 元素
        const header = e.target.closest('.folder-header');
        // 如果找不到 folder-header，直接返回
        if (!header) return;
        const content = header.nextElementSibling;
        header.classList.toggle('open');
        content.style.display = content.style.display !== 'block' ? 'block' : 'none';
    }
    
    function handleFileAddition(folderContent, files) {
        const nonPdfFiles = Array.from(files).filter(file => file.type !== "application/pdf");
        if (nonPdfFiles.length > 0) {
            alert("只接受 PDF 檔案！");
            return;
        }

        const folderName = folderContent.parentNode.querySelector('.folder-header span').textContent;
        for (let file of files) {
            if (getTargetFile(folderContent, file.name)) {
                if (confirm(`資料夾 "${folderName}" 已有一個名為 "${file.name}" 的檔案，是否確定要覆蓋？`)) {
                    console.log("用戶選擇覆蓋檔案。");
                } else {
                    console.log("用戶選擇取消操作。");
                    continue;
                }
            } else {
                const fileName = file.name.substring(0, file.name.lastIndexOf('.')) || file.name;
                const fileElement = document.createElement('div');
                fileElement.className = 'file-link';
                fileElement.draggable = true;
                fileElement.textContent = fileName;
                folderContent.appendChild(fileElement);
            }
            uploadFile(folderName, file);
        }
    }
    
    function createFolder(name, fileNames = []) {
        const folder = document.createElement('div');
        folder.className = 'folder';
        folder.innerHTML = `
            <div class="folder-header">
                <span>${name}</span>
                <button class="upload-btn" title="上傳文件">+</button>
            </div>
            <div class="folder-content"></div>
        `;
        folder.addEventListener('dragover', dragOver);
        folder.addEventListener('dragleave', dragLeave);
        folder.addEventListener('drop', drop);
        folderContainer.appendChild(folder);
    
        const folderHeader = folder.querySelector('.folder-header');
        folderHeader.addEventListener('click', toggleFolder);
    
        const uploadBtn = folder.querySelector('.upload-btn');
        uploadBtn.addEventListener('click', (e) => {
            e.stopPropagation();  // 防止觸發文件夾的折疊/展開
            fileInput.click();
            fileInput.setAttribute('data-target-folder', name);
        });

        const folderContent = folder.querySelector('.folder-content');
        for (let fileName of fileNames) {
            const fileElement = document.createElement('div');
            fileElement.className = 'file-link';
            fileElement.draggable = true;
            fileElement.textContent = fileName;
            folderContent.appendChild(fileElement);
        }
    }
    
    function setFolders() {
        folderContainer.innerHTML = '';
        folderList.forEach(folder => {
            createFolder(folder.name, folder.fileNames);
        });
    }

    function setRecords() {
        mainFuncContainer.innerHTML = '';
        mainFuncContainer.classList.remove('setting');
        mainFuncContainer.classList.add('records');
        if (recordList.length < 1 || recordList[0].title !== '') {
            mainFuncContainer.appendChild(newContainer());
        } else {
            mainFuncContainer.appendChild(refreshContainer());
        }
        recordList.forEach(record => {
            mainFuncContainer.appendChild(RecordContainer(record));
        });
    }

    function setSetting() {
        mainFuncContainer.innerHTML = '';
        mainFuncContainer.classList.remove('records');
        mainFuncContainer.classList.add('setting');
        mainFuncContainer.innerHTML = `
            <div class="file-selector">
                <div class="header">
                    <span>選擇使用文件</span>
                    <div class="select-all-container">
                        <input type="checkbox" id="selectAll" class="select-all-checkbox">
                        <label for="selectAll">全選/全不選</label>
                    </div>
                </div>
                <div id="foldersContainer"></div>
            </div>
            <div class="model-selector">
                <button id="cancelBtn">返回</button>
                <select name="models" id="modelSelect">
                    <option value="">--選擇回應模型--</option>
                </select>
                <button id="submitBtn">送出</button>
            </div>
        `;
        SettingContainer();
    }

    function setProgress(value, max) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        progressBar.value = value;
        progressBar.max = max;
        if (value < max) progressBar.removeAttribute('value');
        progressBar.innerHTML = `${value}/${max}`;
        progressText.textContent = `文件處理進度: ${value}/${max}`;
    }

    function uploadFolder(folderName) {
        fetch(`${API_BASE_URL}/upload/${folderName}`).then(response => response.json())
        .catch(error => console.error('Error upload Folders:', error));
    }

    function uploadFile(folderName, file) {
        const formData = new FormData();
        formData.append('file', file);
        snackbar.innerText = "上傳中";
        snackbar.className = "show";
        fetch(`${API_BASE_URL}/upload/${folderName}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('上傳成功:', data.filename);
                showSnackbar('success');
                fetchFolders();
            } else {
                throw new Error(data.error || '上傳失敗');
            }
        })
        .catch(error => {
            console.error('Error upload File:', error);
            showSnackbar('error');
        });
    }
    
    function moveFile(fileName, folder, newFolder) {
        const data = {
            file_name: fileName,
            folder: folder,
            new_folder: newFolder
        };
        fetch(`${API_BASE_URL}/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response =>  response.json())
        .then(data => {
            if (data.success) {
                console.log('移動成功:', data.filename);
                fetchFolders();
            } else {
                throw new Error(data.error || '移動失敗');
            }
        })
        .catch(error => {
            console.error('Error move File:', error);
            showSnackbar('offline');
        });
    }

    function deleteFolder(folder) {
        fetch(`${API_BASE_URL}/folder`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ folder: folder }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Folder deleted successfully');
                fetchFolders();
            } else {
                throw new Error(data.error || '刪除失敗');
            }
        }).catch(error => {
            console.error('Error delete Folder:', error);
            showSnackbar('offline');
        });
    };

    function deleteFile(folder, fileName) {
        fetch(`${API_BASE_URL}/delete`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ folder: folder, file_name: fileName }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('File deleted successfully');
                fetchFolders();
            } else {
                throw new Error(data.error || '刪除失敗');
            }
        }).catch(error => {
            console.error('Error delete File:', error);
            showSnackbar('offline');
        });
    };

    function fetchFolders() {
        fetch(`${API_BASE_URL}/folders`).then(response => response.json())
        .then(data => {
            folderList = data.folders;
            setFolders();
            setProgress(data.value, data.max);
        }).catch(error => {
            console.error('Error fetching Folders:', error);
            showSnackbar('offline');
        });
    }

    function fetchRecords() {
        fetch(`${API_BASE_URL}/records`).then(response => response.json())
        .then(records => {
            recordList = records;
            setRecords();
        }).catch(error => {
            console.error('Error fetching Records:', error);
            showSnackbar('offline');
        });
    }

    function closeBackend() {
        fetch(`${API_BASE_URL}/terminate`, { method: 'POST' });
        settingsDialog.close();
        showSnackbar('offline');
    }

    function showSnackbar(type) {
        if (type === 'offline') {
            snackbar.innerText = "後端已離線";
            snackbar.className = "offline";
            return;
        } else if (type === 'success') {
            snackbar.innerText = "上傳成功";
            snackbar.className = "show success";
        } else if (type === 'error') {
            snackbar.innerText = "上傳失敗";
            snackbar.className = "show error";
        }
    
        setTimeout(function() { 
            snackbar.className = snackbar.className = "";
        }, 3000);
    }

    function refreshContainer() {
        const div = document.createElement('div');
        div.className = 'record-container refresh';
        div.innerHTML = `
            <div class="refresh-button">
                <div class="refresh-icon"></div>
            </div>
        `;
        div.addEventListener('click', function(event) {
            if (event.target.classList.contains('refresh-button') || event.target.classList.contains('refresh-icon')) {
                fetchRecords();
            }
        });
        return div;
    }

    function newContainer() {
        const div = document.createElement('div');
        div.className = 'record-container new';
        div.innerHTML = `
            <div class="plus-button"></div>
        `;
        div.addEventListener('click', function(event) {
            if (event.target.classList.contains('plus-button')) {
                setSetting();
            }
        });
        return div;
    }
    
    function RecordContainer(record) {
        const div = document.createElement('div');
        div.className = 'record-container';
        if (record.title === '') {
            div.innerHTML = `
                <div class="header"><h2>執行中</h2><progress></progress></div>
                <div class="pdfs">${record.pdfs.map(pdf => pdf.name).join(', ')}</div>
                <div class="content">等待執行完成...</div>
            `;
        } else {
            div.innerHTML = `
                <div class="header">
                    <h2>${record.title}</h2>
                    <div class="heart">${record.isMark ? '❤️' : '🤍'}</div>
                </div>
                <div class="pdfs">${record.pdfs.map(pdf => pdf.name).join(', ')}</div>
                <div class="content">${record.content}</div>
            `;
            div.querySelector('.heart').addEventListener('click', function(e) {
                e.stopPropagation();
                fetch(`${API_BASE_URL}/record/${record.id}/toggle_mark`, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => fetchRecords())
                    .catch(error => console.error('Error toggling mark:', error));
            });
            div.addEventListener('click', function(e) {
                window.open(`${API_BASE_URL}/record/${record.id}`, '_blank')
            });
        }
        return div;
    }
    
    function SettingContainer(choose) {
        fetch(`${API_BASE_URL}/choose`).then(response => response.json())
        .then(data => {
            setProgress(data.value, data.max);
            const folders = data.folders;
            const models = data.models;
            const foldersContainer = document.getElementById('foldersContainer');
            const cancelBtn = document.getElementById('cancelBtn');
            const submitBtn = document.getElementById('submitBtn');
            const selectAllCheckbox = document.getElementById('selectAll');
            const modelSelect = document.getElementById('modelSelect');
            cancelBtn.addEventListener('click', () => {
                fetchRecords();
            });
            submitBtn.addEventListener('click', () => {
                processFiles(choose, modelSelect, getSelectedFiles());
            });

            models.forEach((model, index) => {
                const option = document.createElement('option');
                option.value = index;
                option.textContent = model;
                modelSelect.appendChild(option);
            });

            folders.forEach((folder, index) => {
                const folderItem = document.createElement('div');
                folderItem.className = 'folder-item';
                folderItem.innerHTML = `
                    <div class="folder-header">
                        <input type="checkbox" id="folder${index}" class="folder-checkbox">
                        <label for="folder${index}">${folder.name}</label>
                        <span class="toggle-btn">▼</span>
                    </div>
                    <div class="folder-content">
                        ${folder.fileNames.map((fileName, fileIndex) => `
                            <div class="file-item">
                                <input type="checkbox" id="file${index}-${fileIndex}" class="file-checkbox" data-folder="${folder.name}" data-file="${fileName}">
                                <label for="file${index}-${fileIndex}">${fileName}</label>
                            </div>
                        `).join('')}
                    </div>
                `;
                foldersContainer.appendChild(folderItem);
        
                // 添加資料夾切換功能
                const toggleBtn = folderItem.querySelector('.toggle-btn');
                const folderContent = folderItem.querySelector('.folder-content');
                toggleBtn.addEventListener('click', () => {
                    folderContent.style.display = folderContent.style.display === 'none' ? 'block' : 'none';
                    toggleBtn.textContent = folderContent.style.display === 'none' ? '▼' : '▲';
                });
        
                // 資料夾 checkbox 控制檔案 checkbox
                const folderCheckbox = folderItem.querySelector('.folder-checkbox');
                const fileCheckboxes = folderItem.querySelectorAll('.file-checkbox');
                folderCheckbox.addEventListener('change', () => {
                    fileCheckboxes.forEach(checkbox => checkbox.checked = folderCheckbox.checked);
                    updateSelectAllCheckbox();
                });
        
                // 檔案 checkbox 改變時更新資料夾和全選 checkbox
                fileCheckboxes.forEach(checkbox => {
                    checkbox.addEventListener('change', () => {
                        folderCheckbox.checked = Array.from(fileCheckboxes).every(cb => cb.checked);
                        updateSelectAllCheckbox();
                    });
                });
            });
        
            const allCheckboxes = document.querySelectorAll('.folder-checkbox, .file-checkbox');
        
            // 全選/全不選 checkbox 功能
            selectAllCheckbox.addEventListener('change', () => {
                allCheckboxes.forEach(checkbox => checkbox.checked = selectAllCheckbox.checked);
            });
        
            // 更新全選 checkbox 狀態的函數
            function updateSelectAllCheckbox() {
                selectAllCheckbox.checked = Array.from(allCheckboxes).every(checkbox => checkbox.checked);
            }

            // 收集被選擇的檔案
            function getSelectedFiles() {
                const selectedFiles = [];
                const fileCheckboxes = document.querySelectorAll('.file-checkbox:checked');
                fileCheckboxes.forEach(checkbox => {
                    const folderName = checkbox.getAttribute('data-folder');
                    const fileName = checkbox.getAttribute('data-file');
                    selectedFiles.push(`${folderName}/${fileName}`);
                });
                return selectedFiles;
            }
        }).catch(error => {
            console.error('Error fetching Choose:', error);
            showSnackbar('offline');
        });
    }
    
    function processFiles(choose, modelSelect, files) {
        if (files.length < 1 && choose !== '開始對話') {
            alert('請選擇文件，或是等待文件預處理完成');
            return;
        }
        const selectedIndex = modelSelect.selectedIndex - 1;
        if (selectedIndex >= 0) {
            fetch(`${API_BASE_URL}/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    choose: choose,
                    model_index: selectedIndex,
                    files: files
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(data.message);
                } else {
                    alert('有對話正在執行中，執行完畢後才能開啟新的對話。');
                }
                fetchRecords();
            })
            .catch(error => console.error('Error processing files:', error));
        } else {
            alert("請選擇回應模型");
        }
    }
});