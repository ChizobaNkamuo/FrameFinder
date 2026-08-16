import { useState } from "react";
import "./SearchBar.css";
import "./VideoStatus.css";
import { Search } from "lucide-react";

type SearchBarProps = {
    onSearch: (query: string) => void;
    processing: boolean
};

export default function SearchBar({ onSearch, processing }: SearchBarProps) {
    const [searchQuery, setSearchQuery] = useState<string>("");

    return (
        <div className="search-bar">
            <input
                type="text"
                placeholder="Search..."
                onKeyDown={(event) => {
                    if (event.key === "Enter" && !processing) {
                        onSearch(searchQuery);
                    }
                }}
                onChange={(event) => setSearchQuery(event.currentTarget.value.toLowerCase())}
            />
            
            <span className="status-spinner" />
            <button type="button" aria-label="Search"
               onClick={() => {
                    if (!processing) {
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