var app = new Vue({
    delimiters: ["#{", "}"],
    el: "#app",
    data: {
        user: "-1",
        usersAll: [],
        usersInclude: [],
        keysAll: {},
        keysInclude: {},
        targetKey: null,
        goal: "0",
        mode: "lin",
        notification: "",
        information: [{
            key: "",
            value: 0,
            type: "Number"
        }]
    },
    computed: {
        validKeys: function() {
            var validIds = this.usersInclude.map(function(user) {
                return user.id;
            });

            var self = this;
            var keys = {};
            var valids = Object.keys(self.keysAll).filter(function(key) {
                var valid = true;
                validIds.forEach(function(vid) {
                    if (!valid) return;
                    valid = self.keysAll[key].indexOf(vid) > -1;
                });
                
                return valid;
            }).forEach(function(key) {
                keys[key] = self.keysAll[key];
            });
            return keys;
        },
        validKeysInclude: function () {
            var validIds = this.usersInclude.map(function (user) {
                return user.id;
            });

            var self = this;
            var keys = {};
            var valids = Object.keys(self.keysInclude).filter(function (key) {
                var valid = true;
                validIds.forEach(function (vid) {
                    if (!valid) return;
                    valid = self.keysInclude[key].indexOf(vid) > -1;
                });

                return valid;
            }).forEach(function (key) {
                keys[key] = self.keysInclude[key];
            });
            return keys;
        }
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
        userIn: function (uid) {
            var move = -1;
            this.usersAll.forEach(function (user, i) {
                if (user.id === uid) {
                    move = i;
                }
            });
            if (move > -1) {
                this.usersInclude.push(this.usersAll[move]);
                this.usersAll.splice(move, 1);
            }
        },
        userOut: function (uid) {
            var move = -1;
            this.usersInclude.forEach(function (user, i) {
                if (user.id === uid) {
                    move = i;
                }
            });
            if (move > -1) {
                this.usersAll.push(this.usersInclude[move]);
                this.usersInclude.splice(move, 1);
            }
        },
        keyIn: function (id) {
            this.$set(this.keysInclude, id, this.keysAll[id]);
            this.$delete(this.keysAll, id);
        },
        keyOut: function (id) {
            this.$set(this.keysAll, id, this.keysInclude[id]);
            this.$delete(this.keysInclude, id);
        },
        toggleLock: function(id) {
            if (this.targetKey === id) {
                this.targetKey = null;
            } else {
                this.targetKey = id;
            }
        },
        deleteUser: function () {
            if (!window.confirm("Are you sure?")) return false;

            axios.post("/delete", {
                user: this.user
            }).then(function (res) {
                console.log(res.data.success);

                if (res.data.success) {
                    window.location.reload();
                }
            });
        },
        think: function() {
            axios.post("/think", {
                users: this.usersInclude.map(function(user) {
                    return user.id;
                }).join(","),
                keys: Object.keys(this.validKeysInclude).join(","),
                goal: this.goal, // +, -, 0
                mode: this.mode, // exp, lin, log
                target: this.targetKey
            }).then(function (res) {
                if (res.data.success) {
                    UIkit.notification({
                        message: "Decided on: " + res.data.decision,
                        status: "primary",
                        pos: "top-right",
                        timeout: 5000
                    });
                }
            });
        }
    }
});