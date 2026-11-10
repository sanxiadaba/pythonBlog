// 后台编辑器：Markdown 实时预览、工具条、图片上传。
(() => {
  const form = document.getElementById("article-form");
  const body = document.getElementById("body");
  const preview = document.getElementById("preview");
  const status = document.getElementById("editor-status");
  const fileInput = document.getElementById("image-file");
  const csrfToken = form.querySelector('input[name="csrf_token"]').value;

  const render = () => {
    preview.innerHTML = marked.parse(body.value || "");
    preview.querySelectorAll("pre code").forEach((block) => hljs.highlightElement(block));
  };

  let timer = null;
  const draftKey = `draft:${location.pathname}`;

  body.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      render();
      localStorage.setItem(draftKey, body.value);
    }, 150);
  });
  render();

  // 正文为空说明是新建文章，直接恢复上次没保存的草稿；已有内容时不动它。
  const draft = localStorage.getItem(draftKey);
  if (draft && !body.value.trim()) {
    body.value = draft;
    render();
    status.textContent = "已恢复上次未保存的草稿";
  }

  form.addEventListener("submit", () => localStorage.removeItem(draftKey));

  const insert = (text) => {
    const start = body.selectionStart;
    body.setRangeText(text, start, body.selectionEnd, "end");
    body.focus();
    render();
  };

  const wrap = (before, after) => {
    const start = body.selectionStart;
    const end = body.selectionEnd;
    const selected = body.value.slice(start, end);
    body.setRangeText(before + selected + after, start, end, "end");
    body.setSelectionRange(start + before.length, start + before.length + selected.length);
    body.focus();
    render();
  };

  const prefixLines = (prefix) => {
    const start = body.selectionStart;
    const lineStart = body.value.lastIndexOf("\n", start - 1) + 1;
    const end = Math.max(body.selectionEnd, start);
    const block = body.value.slice(lineStart, end);
    const lines = (block || "")
      .split("\n")
      .map((line) => prefix + line)
      .join("\n");
    body.setRangeText(lines || prefix, lineStart, end, "end");
    body.focus();
    render();
  };

  document.querySelectorAll(".editor-toolbar button[data-wrap]").forEach((button) => {
    button.addEventListener("click", () => {
      const marker = button.dataset.wrap;
      wrap(marker, marker);
    });
  });

  document.querySelectorAll(".editor-toolbar button[data-block]").forEach((button) => {
    button.addEventListener("click", () => {
      const open = button.dataset.block;
      const close = button.dataset.blockEnd;
      if (close) {
        const start = body.selectionStart;
        const selected = body.value.slice(start, body.selectionEnd);
        body.setRangeText(open + selected + close, start, body.selectionEnd, "end");
        body.focus();
        render();
      } else {
        prefixLines(open);
      }
    });
  });

  document.querySelectorAll(".editor-toolbar button[data-link]").forEach((button) => {
    button.addEventListener("click", () => {
      const start = body.selectionStart;
      const selected = body.value.slice(start, body.selectionEnd) || "链接文字";
      const text = `[${selected}]()`;
      body.setRangeText(text, start, body.selectionEnd, "end");
      const urlPos = start + text.length - 1;
      body.setSelectionRange(urlPos, urlPos);
      body.focus();
      render();
    });
  });

  document.getElementById("upload-image").addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    status.textContent = "上传中…";
    const data = new FormData();
    data.append("image", file);
    try {
      const response = await fetch("/admin/upload", {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
        body: data,
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "上传失败");
      insert(`![${file.name.replace(/\.[^.]+$/, "")}](${result.url})`);
      status.textContent = "图片已插入";
    } catch (error) {
      status.textContent = error.message;
    } finally {
      fileInput.value = "";
    }
  });

  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "s") {
      event.preventDefault();
      form.requestSubmit();
    }
  });
})();
