var app = new Vue({
    delimiters: ["#{", "}"],
    el: "#app",
    data: {
        user: "-1",
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
        },
        deleteUser: function() {
            if (!window.confirm("Are you sure?")) return false;
            
            axios.post("/delete", {
                user: this.user
            }).then(function(res) {
                console.log(res.data.success);
                
                if (res.data.success) {
                    window.location.reload();
                }
            });
        }
    }
});