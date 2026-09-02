import { useState } from "react";
import "./SearchBar.css";
import "./VideoStatus.css";
import { Search } from "lucide-react";

type SearchBarProps = {
    onSearch: (query: string) => void;
    processing: boolean
    searchOnChange: boolean
};

export default function SearchBar({ onSearch, processing, searchOnChange }: SearchBarProps) {
    const [searchQuery, setSearchQuery] = useState<string>("");

    return (
        <div className="search-bar">
            <input
                type="text"
                placeholder="Search..."
                onKeyDown={(event) => {
                    if (!searchOnChange && event.key === "Enter" && !processing) {
                        onSearch(searchQuery);
                    }
                }}
                onChange={(event) => {
                    var latestSearchQuery = event.currentTarget.value.toLowerCase();
                    setSearchQuery(latestSearchQuery);

                    if (searchOnChange) {
                        onSearch(latestSearchQuery);
                    }
                }}
            />
            
            <span className="status-spinner" />
            <button type="button" aria-label="Search"
               onClick={() => {
                    if (!searchOnChange && !processing) {
                        onSearch(searchQuery);
                    }
                }}            
            >
                {processing ?
                <span className="search-status-spinner" />:
                <Search />
                }
            </button>
        </div>
    );
}