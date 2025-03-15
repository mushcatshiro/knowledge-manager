/*
  const below are for rendering, can be ignored if not needed
  simplest editor.js only concerns about block <-> textarea
*/

const mdBlockToHTML = new Map([
    ['#', 'h1'],
    ['##', 'h2'],
    ['###', 'h3'],
    ['####', 'h4'],
    ['#####', 'h5'],
    ['######', 'h6'],
    ['```', 'code'],
    ['$$', 'math'],
    ['>', 'blockquote'],
]);

const htmlToMdBlock = new Map([
    ['h1', '#'],
    ['h2', '##'],
    ['h3', '###'],
    ['h4', '####'],
    ['h5', '#####'],
    ['h6', '######'],
    ['code', '```'],
    ['math', '$$'],
    ['blockquote', '>'],
]);

function registerElement(el) {
    el.addEventListener('click', onMouseClick);
    el.addEventListener('mouseover', onMouseHover);
    el.addEventListener('mouseout', onMouseOut);
}

function onAddButtonClick(event) {
    event.stopPropagation(); // Prevent triggering the parent's click event
    let blogContent = document.getElementById('blog-content');
    let children = Array.from(blogContent.children);
    let currentElement = this.parentElement;
    let index = children.indexOf(currentElement);

    let newElm = document.createElement('textarea');
    if (index === children.length - 1) {
        // If it's the last element, append the textarea at the end
        blogContent.appendChild(newElm);
    } else {
        // Otherwise, insert the textarea after the current element
        blogContent.insertBefore(newElm, children[index + 1]);
    }
}

function onDeleteButtonClick(event) {
    event.stopPropagation(); // Prevent triggering the parent's click event
    let blogContent = document.getElementById('blog-content');
    let currentElement = this.parentElement;
    blogContent.removeChild(currentElement);
}

function registerElements() {
    let elm = document.getElementById('blog-content');
    for (const child of elm.children) {
        registerElement(child);
    }
}

function registerButton() {
    let elm = document.getElementById('edit-button');
    elm.addEventListener('click', onClickCommitEdit);
}

function onMouseHover() {
    this.style.backgroundColor = 'red';
    // let blogContent = document.getElementById('blog-content');
    // let children = Array.from(blogContent.children);
    // let index = children.indexOf(this);
    // console.log('Hovered element index:', index);

    // Create and append "+" button and delete button
    // if (!this.querySelector('.add-button')) {
    //     // Create and append "+" button and delete button
    //     let addButton = document.createElement('button');
    //     addButton.textContent = '+';
    //     addButton.className = 'add-button';
    //     addButton.addEventListener('click', onAddButtonClick);
    //     blogContent.insertBefore(addButton, children[index]);
        // if (index === children.length - 1) {
        //     // If it's the last element, append the textarea at the end
        //     blogContent.appendChild(addButton);
        // } else {
        //     // Otherwise, insert the textarea after the current element
        //     blogContent.insertBefore(addButton, children[index + 1]);
        // }
    // }
}
function onMouseOut() {
    this.style.backgroundColor = '';
    // let addButton = document.getElementsByClassName('add-button');
    // for (let i = 0; i < addButton.length; i++) {
    //     let button = addButton[i];
    //     button.remove();
    // }
}

function onMouseClick() {
    let newElm = document.createElement('textarea');
    newElm.innerHTML = this.innerHTML;
    newElm.name = this.tagName;
    this.parentElement.replaceChild(newElm, this);
}

function onClickCommitEdit() {
    // let targetElms = document.getElementsByTagName('textarea');
    let targetElms = Array.from(document.getElementsByTagName('textarea'));
    for (let elm of targetElms) {
        // split elm.value by '\n\n'
        let children = new Set();
        let blocks = elm.value.split('\n\n');
        console.log(blocks);
        for (let block of blocks) {
            let newElm = document.createElement(elm.name);
            let blockType = block.split(' ')[0];
            let blockContent = block.slice(blockType.length + 1);
            let blockElm = document.createElement(mdBlockToHTML.get(blockType) || 'p');
            blockElm.textContent = blockContent;
            children.add(blockElm);
        }
        // newElm.textContent = elm.value;
        // registerElement(newElm);
        // elm.parentNode.replaceChild(newElm, elm);
        elm.parentNode.replaceChildren(...children);
    }
}

function onClickUpload() {
    onClickCommitEdit();
}

registerElements();
registerButton();

/*
  - consider removing empty textareas
*/
