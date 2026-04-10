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
  const pinFontValue = document.getElementById("pin-font-value");
  const qrScaleMin = qrScaleSlider ? parseFloat(qrScaleSlider.min) || 0 : 0;
  const qrScaleMax = qrScaleSlider ? parseFloat(qrScaleSlider.max) || 1 : 1;
  const qrScaleRange = Math.max(qrScaleMax - qrScaleMin, 0.0001);
  const pinFontMin = pinFontSlider ? parseFloat(pinFontSlider.min) || 0 : 0;
  const pinFontMax = pinFontSlider ? parseFloat(pinFontSlider.max) || 1 : 1;
  const pinFontRange = Math.max(pinFontMax - pinFontMin, 0.0001);

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
    const rect = img.getBoundingClientRect();
    const w = rect.width;
    const h = rect.height;
  
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

  function sliderPercent(slider, min, range) {
    if (!slider) return 0;
    const value = parseFloat(slider.value || slider.defaultValue || min);
    return Math.round(Math.max(0, Math.min(1, (value - min) / range)) * 99) + 1;
  }

  function updateSliderLabel(slider, label, min, range) {
    if (!slider || !label) return;
    const percent = sliderPercent(slider, min, range);
    label.textContent = `${percent}%`;
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
    const imgRect = img.getBoundingClientRect();
    const qrRect = qrBox.getBoundingClientRect();
  
    qrXInput.value = ((qrRect.left - imgRect.left) / imgRect.width).toFixed(6);
    qrYInput.value = ((qrRect.top - imgRect.top) / imgRect.height).toFixed(6);
  }
  
  function savePinPosition() {
    const imgRect = img.getBoundingClientRect();
    const pinRect = pinBox.getBoundingClientRect();
  
    pinXInput.value = ((pinRect.left - imgRect.left) / imgRect.width).toFixed(6);
    pinYInput.value = ((pinRect.top - imgRect.top) / imgRect.height).toFixed(6);
  }
  qrScaleSlider.addEventListener("input", function () {
    qrScaleInput.value = this.value;
    updateSliderLabel(qrScaleSlider, qrScaleValue, qrScaleMin, qrScaleRange);
    placeElements();
    saveQrPosition();
  });

  pinFontSlider.addEventListener("input", function () {
    pinFontInput.value = this.value;
    updateSliderLabel(pinFontSlider, pinFontValue, pinFontMin, pinFontRange);
    pinBox.style.fontSize = this.value + "px";
  });

  img.addEventListener("load", function () {
    qrXInput.value = qrXInput.value || dataQrX;
    qrYInput.value = qrYInput.value || dataQrY;
    qrScaleInput.value = qrScaleInput.value || dataQrScale;
    pinXInput.value = pinXInput.value || dataPinX;
    pinYInput.value = pinYInput.value || dataPinY;
    pinFontInput.value = pinFontInput.value || dataPinFont;

    updateSliderLabel(qrScaleSlider, qrScaleValue, qrScaleMin, qrScaleRange);
    updateSliderLabel(pinFontSlider, pinFontValue, pinFontMin, pinFontRange);

    placeElements();

    makeDraggable(qrBox, saveQrPosition);
    makeDraggable(pinBox, savePinPosition);
  });

  if (img.complete) {
    img.dispatchEvent(new Event("load"));
  }
});
