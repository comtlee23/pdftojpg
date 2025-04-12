// static/script.js

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("uploadForm");
    const fileInput = document.getElementById("pdfFile");

    form.addEventListener("submit", function (e) {
        e.preventDefault(); // 폼 기본 동작 방지

        const file = fileInput.files[0];
        if (!file) {
            alert("PDF 파일을 선택해주세요.");
            return;
        }

        const formData = new FormData();
        formData.append("pdf_file", file);

        // 서버에 파일 업로드 및 변환 요청
        fetch("/convert", {
            method: "POST",
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("서버 응답 오류");
            }
            return response.json();
        })
        .then(data => {
            if (data.success && data.download_url) {
                // 서버에서 받은 ZIP 파일 경로에서 파일명 추출
                const urlParts = data.download_url.split('/');
                const filename = urlParts[urlParts.length - 1];

                // 다운로드 페이지로 이동
                window.location.href = `/download/${filename}`;
            } else {
                alert("변환에 실패했습니다: " + (data.error || "알 수 없는 오류"));
            }
        })
        .catch(error => {
            console.error("에러 발생:", error);
            alert("파일 변환 중 오류가 발생했습니다.");
        });
    });
});
