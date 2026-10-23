function getScrollPercent() {
  const totalHeight = document.body.scrollHeight - window.innerHeight;
  const scrolled = window.scrollY;
  return (scrolled / totalHeight) * 100;
}
const scrollProgressBar = document.getElementById("scroll-progress-bar");

document.onscroll = function () {
  var scrollPercent = Math.min(100, Math.max(0, Math.round(getScrollPercent())));
  scrollProgressBar.style.width = scrollPercent + "%";
  scrollProgressBar.ariaValueNow = scrollPercent;
};
