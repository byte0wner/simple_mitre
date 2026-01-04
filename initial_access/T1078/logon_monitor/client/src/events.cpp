#include <iostream>
#include <regex>
#include "events.h"
#include "utils.h"

std::string GetFieldByName(std::wstring field_name, std::wstring & xml) {
    std::wstring regex_format;

    if (field_name == L"SystemTime") {
        regex_format = L"\\<TimeCreated " + field_name + L"='([^\\>]+)'/\\>";
    } else {
        regex_format = L"\\<Data Name='" + field_name + L"'\\>([^\\<]+)\\</Data\\>";
    }
    std::wregex pattern(regex_format);
    std::wsmatch match;
    if (std::regex_search(xml, match, pattern)) {
        return ws2s(match[1].str());
    } else {
        return "";
    }
}