// static/script.js

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("uploadForm");
    const fileInput = document.getElementById("pdfFile");

    form.addEventListener("submit", function (e) {
        e.preventDefault(); // 새로고침 방지

        const file = fileInput.files[0];

        if (!file) {
            alert("PDF 파일을 선택해주세요.");
            return;
        }

        const formData = new FormData();
        formData.append("pdf_file", file);

        // 서버에 PDF 업로드
        fetch("/convert", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.download_url) {
                // 파일 이름 추출 (예: /static/output/converted_20250412100000.jpg → converted_20250412100000.jpg)
                const urlParts = data.download_url.split('/');
                const filename = urlParts[urlParts.length - 1];

                // 다운로드 페이지로 리다이렉트
                window.location.href = `/download/${filename}`;
            } else {
                alert("변환에 실패했습니다: " + (data.error || "알 수 없는 오류"));
            }
        })
        .catch(error => {
            console.error("에러:", error);
            alert("서버와 통신 중 오류가 발생했습니다.");
        });
    });
});
