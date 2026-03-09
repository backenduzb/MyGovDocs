document.addEventListener("DOMContentLoaded", function () {
  const root = document.querySelector(".pdf-editor-root");
  if (!root) return;

  const stage = document.getElementById("pdf-editor-stage");
  const img = document.getElementById("pdf-preview-image");
  const qrBox = document.getElementById("qr-box");
  const pinBox = document.getElementById("pin-box");

  const qrScaleSlider = document.getElementById("qr-scale-slider");
  const pinFontSlider = document.getElementById("pin-font-slider");

  const qrXInput = document.getElementById("id_qr_x");
  const qrYInput = document.getElementById("id_qr_y");
  const qrScaleInput = document.getElementById("id_qr_scale");
  const pinXInput = document.getElementById("id_pin_x");
  const pinYInput = document.getElementById("id_pin_y");
  const pinFontInput = document.getElementById("id_pin_font_size");
  const qrScaleValue = document.getElementById("qr-scale-value");
  const qrScaleProgress = document.getElementById("qr-scale-progress");
  const qrScaleMin = qrScaleSlider ? parseFloat(qrScaleSlider.min) || 0 : 0;
  const qrScaleMax = qrScaleSlider ? parseFloat(qrScaleSlider.max) || 1 : 1;
  const qrScaleRange = Math.max(qrScaleMax - qrScaleMin, 0.0001);

  const dataQrX = parseFloat(root.dataset.qrX || 0.78);
  const dataQrY = parseFloat(root.dataset.qrY || 0.78);
  const dataQrScale = parseFloat(root.dataset.qrScale || 0.14);
  const dataPinX = parseFloat(root.dataset.pinX || 0.68);
  const dataPinY = parseFloat(root.dataset.pinY || 0.92);
  const dataPinFont = parseFloat(root.dataset.pinFont || 22.5);

  function clamp(v, min, max) {
    return Math.max(min, Math.min(max, v));
  }

  function placeElements() {
    const w = img.clientWidth;
    const h = img.clientHeight;

    const qrScale = parseFloat(qrScaleInput.value || dataQrScale);
    const qrSize = Math.min(w, h) * qrScale;

    qrBox.style.width = qrSize + "px";
    qrBox.style.height = qrSize + "px";
    qrBox.style.left = parseFloat(qrXInput.value || dataQrX) * w + "px";
    qrBox.style.top = parseFloat(qrYInput.value || dataQrY) * h + "px";

    pinBox.style.left = parseFloat(pinXInput.value || dataPinX) * w + "px";
    pinBox.style.top = parseFloat(pinYInput.value || dataPinY) * h + "px";
    pinBox.style.fontSize =
      parseFloat(pinFontInput.value || dataPinFont) + "px";
  }

  function updateScaleIndicator(value) {
    if (!qrScaleValue && !qrScaleProgress) return;
    let ratio = (parseFloat(value) - qrScaleMin) / qrScaleRange;
    ratio = Math.max(0, Math.min(1, ratio));
    const percent = Math.round(ratio * 99) + 1;
    if (qrScaleValue) {
      qrScaleValue.textContent = percent;
    }
    if (qrScaleProgress) {
      qrScaleProgress.value = percent;
    }
  }

  function makeDraggable(el, onStop) {
    let dragging = false;
    let startX = 0,
      startY = 0,
      origLeft = 0,
      origTop = 0;

    el.addEventListener("mousedown", function (e) {
      dragging = true;
      startX = e.clientX;
      startY = e.clientY;
      origLeft = el.offsetLeft;
      origTop = el.offsetTop;
      e.preventDefault();
    });

    document.addEventListener("mousemove", function (e) {
      if (!dragging) return;

      const dx = e.clientX - startX;
      const dy = e.clientY - startY;

      let newLeft = origLeft + dx;
      let newTop = origTop + dy;

      newLeft = clamp(newLeft, 0, stage.clientWidth - el.offsetWidth);
      newTop = clamp(newTop, 0, stage.clientHeight - el.offsetHeight);

      el.style.left = newLeft + "px";
      el.style.top = newTop + "px";
    });

    document.addEventListener("mouseup", function () {
      if (!dragging) return;
      dragging = false;
      onStop();
    });
  }

  function saveQrPosition() {
    qrXInput.value = (qrBox.offsetLeft / img.clientWidth).toFixed(6);
    qrYInput.value = (qrBox.offsetTop / img.clientHeight).toFixed(6);
  }

  function savePinPosition() {
    pinXInput.value = (pinBox.offsetLeft / img.clientWidth).toFixed(6);
    pinYInput.value = (pinBox.offsetTop / img.clientHeight).toFixed(6);
  }

  qrScaleSlider.addEventListener("input", function () {
    qrScaleInput.value = this.value;
    updateScaleIndicator(this.value);
    placeElements();
    saveQrPosition();
  });

  pinFontSlider.addEventListener("input", function () {
    pinFontInput.value = this.value;
    pinBox.style.fontSize = this.value + "px";
  });

  img.addEventListener("load", function () {
    qrXInput.value = qrXInput.value || dataQrX;
    qrYInput.value = qrYInput.value || dataQrY;
    qrScaleInput.value = qrScaleInput.value || dataQrScale;
    pinXInput.value = pinXInput.value || dataPinX;
    pinYInput.value = pinYInput.value || dataPinY;
    pinFontInput.value = pinFontInput.value || dataPinFont;

    updateScaleIndicator(qrScaleInput.value);

    placeElements();

    makeDraggable(qrBox, saveQrPosition);
    makeDraggable(pinBox, savePinPosition);
  });

  if (img.complete) {
    img.dispatchEvent(new Event("load"));
  }
});
