var app = new Vue({
    delimiters: ["#{", "}"],
    el: "#app",
    data: {
        test: [],
        information: [{
            key: "",
            value: 0,
            type: "Number"
        }]
    },
    methods: {
        percent: function(index) {
            return (this.information[index].value / 100).toFixed(2);
        },
        addInformation: function() {
            this.information.push({
                key: "",
                value: 0,
                type: "Number"
            })
        }
    }
});