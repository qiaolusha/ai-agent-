package com.qiao.model;

import java.util.List;

public class Candidate {
    private String name;
    private String email;
    public List<String> skills;

    // Getter & Setter
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    @Override
    public String toString() {
        return "Candidate{name='" + name + "', email='" + email + "'}";
    }
}
