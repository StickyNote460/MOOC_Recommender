// 课程搜索功能
async function searchCourse() {
    const courseName = document.getElementById('courseInput').value.trim()
    if (!courseName) return

    try {
        // 调用Django API
        const response = await fetch(`/api/recommend?course=${encodeURIComponent(courseName)}`)
        const data = await response.json()

        // 显示推荐路径
        displayRecommendation(data)

        // 更新可视化
        if (data.graph_data) {
            drawDependencyGraph(data.graph_data)
        }
    } catch (error) {
        showError('获取推荐失败，请稍后重试')
    }
}

// 显示推荐结果
function displayRecommendation(data) {
    const resultDiv = document.getElementById('pathResult')

    if (data.error) {
        resultDiv.innerHTML = `<div class="error-msg">${data.error}</div>`
        return
    }

    resultDiv.innerHTML = `
        <div class="path-display">
            <span class="path-badge">推荐路径</span>
            ${data.path || '暂无推荐路径'}
        </div>
        ${data.description ? `<p class="path-desc">${data.description}</p>` : ''}
    `
}

// 错误处理
function showError(msg) {
    const resultDiv = document.getElementById('pathResult')
    resultDiv.innerHTML = `<div class="error-msg">⚠️ ${msg}</div>`
}