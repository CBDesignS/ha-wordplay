/**
 * MINIMAL TEST PANEL for H.A WordPlay
 * Just shows "HA WordPlay Works!" to verify JS loading
 */

// Simple panel content - no imports, no complex code
const panelContent = `
<div style="
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: var(--card-background-color, #ffffff);
  color: var(--primary-text-color, #000000);
  font-family: var(--primary-font-family, sans-serif);
  padding: 20px;
">
  <h1 style="
    font-size: 48px;
    margin: 20px 0;
    color: var(--primary-color, #03a9f4);
  ">🎮 HA WordPlay Works! 🎮</h1>
  
  <p style="
    font-size: 18px;
    text-align: center;
    margin: 10px 0;
    color: var(--secondary-text-color, #666);
  ">JavaScript is loading successfully!</p>
  
  <div style="
    background: var(--primary-color, #03a9f4);
    color: white;
    padding: 15px 30px;
    border-radius: 8px;
    margin: 20px 0;
    font-weight: bold;
  ">Panel Registration Working ✅</div>
  
  <div style="
    border: 2px solid var(--divider-color, #e0e0e0);
    border-radius: 12px;
    padding: 20px;
    margin: 20px 0;
    background: var(--secondary-background-color, #f5f5f5);
    max-width: 600px;
  ">
    <h3 style="margin-top: 0;">🔧 Next Steps:</h3>
    <ul style="text-align: left; line-height: 1.6;">
      <li>✅ JavaScript file loads correctly</li>
      <li>✅ Panel renders in Home Assistant</li>
      <li>✅ Styling works with HA theme</li>
      <li>🎯 Ready for full WordPlay interface!</li>
    </ul>
  </div>
  
  <div style="
    font-size: 14px;
    color: var(--secondary-text-color, #999);
    margin-top: 20px;
  ">
    File: wordplay_panel_test.js<br>
    Path: /hacsfiles/ha_wordplay/wordplay_panel_test.js
  </div>
</div>
`;

// Simple DOM manipulation - no fancy frameworks
document.addEventListener('DOMContentLoaded', function() {
  console.log('🎮 WordPlay Test Panel: DOM loaded');
  
  // Find the panel root
  const panelRoot = document.querySelector('ha-panel-wordplay');
  if (panelRoot) {
    console.log('🎮 WordPlay Test Panel: Found panel root');
    panelRoot.innerHTML = panelContent;
  } else {
    console.log('🎮 WordPlay Test Panel: No panel root found, adding to body');
    document.body.innerHTML = panelContent;
  }
});

// Also try immediate execution
console.log('🎮 WordPlay Test Panel: Script loaded immediately');

// Try to set content right away
setTimeout(() => {
  const panelRoot = document.querySelector('ha-panel-wordplay') || document.body;
  if (panelRoot) {
    panelRoot.innerHTML = panelContent;
    console.log('🎮 WordPlay Test Panel: Content set via timeout');
  }
}, 100);

console.log('🎮 WordPlay Test Panel: Script execution complete');