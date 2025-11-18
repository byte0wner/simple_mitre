package com.example.happybirthday

object BlockedNumbers {
    private val BLOCKED = setOf(
        "79161234567",
        "88005553535",
        "79161881212"
    )

    fun contains(number: String): Boolean {
        return BLOCKED.contains(normalize(number))
    }

    // we need to normalize various number formats like
    // + 7 (916) 122 12 12
    // +79161221212
    // 79161221212
    // to only numbers, like this: 79161221212
    private fun normalize(number: String): String {
        return number.replace("[^0-9]".toRegex(), "")
    }
}