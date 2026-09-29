const overlay = document.getElementById('overlay');

const users = [
  { id: 1, name: 'Noraノラ', avatar: 'https://cdn.discordapp.com/avatars/723840267899240490/5d9e03875562ddab55c8254c205b6c04.webp?size=160', speaking: true },
  { id: 2, name: 'ほんひま', avatar: 'https://example.com/honhima.png', speaking: false },
  { id: 3, name: '社築', avatar: 'https://example.com/yashiro.png', speaking: false },
  { id: 4, name: '戌亥とこ', avatar: 'https://example.com/toko.png', speaking: true },
];

function render() {
  overlay.innerHTML = '';

    const sorted = users; // сохраняем порядок


  for (const user of sorted) {
    const div = document.createElement('div');
    div.className = 'user' + (user.speaking ? ' speaking' : '');
    div.innerHTML = `
      <img class="avatar" src="${user.avatar}">
      <span class="name">${user.name}</span>
    `;
    overlay.appendChild(div);
  }
}

render();