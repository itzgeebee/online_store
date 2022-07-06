'useStrict';

const minPrice = document.querySelector("#min-price");
const maxPrice = document.querySelector('#max-price');

// const validateFilter = (min, max) => 
document.querySelector(`#filter-btn`).addEventListener(`click`, (e) => {
    e.preventDefault()
    if (minPrice === "" || maxPrice === "") return;
    if (minPrice >= maxPrice) return;

    fetch(`/filter`, {
        method: `POST`
    })
        .then(function (response) {
            return response.json()
        })
        .then(function (jsonResponse) {
            console.log(jsonResponse)
            if (jsonResponse) {
                console.log("success")
                window.location.href = "/cart"
            }
        })
}

})