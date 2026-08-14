import Link from "next/link";
import { useRouter } from "next/router";
import clsx from "clsx";

export default function WorkList({ allPosts, activeSlug }) {
  const {
    query: { slug },
  } = useRouter();

  return (
    <div className="w-full">
      <h2 className="font-medium text-black text-2xl mb-4 mt-4">Side projects</h2>
      <div className="last:!border-b-0">
        {allPosts?.map((post) => (
          <div key={post.slug}>
            <Link href={`/projects/${post.slug}`} className="w-full">
              <article
                className={clsx(
                  "flex border-dashed font-medium w-full py-3 md:py-[12px] dark:text-white border-b border-gray-200 hover:border-gray-400 dark:border-gray-700 dark:hover:border-gray-500 flex-row",
                  activeSlug === post.slug ? "text-black" : "text-gray-800 "
                )}
              >
                {post?.icon ? (
                  <img
                    src={post.icon}
                    alt={post.title}
                    className="w-6 h-6 rounded-full shadow-[0_1px_3px_rgba(0,0,0,0.1)] dark:border-gray-800"
                  />
                ) : (
                  <div className="flex items-center justify-center w-6 h-6 text-lg font-bold text-white bg-black border border-gray-100 rounded-full dark:border-gray-800">
                    {post.title?.slice(0, 1)}
                  </div>
                )}
                <h2 className="font-semibold ml-3">{post.title}</h2>
                <div className="ml-auto flex gap-2 items-center flex-wrap justify-end max-w-[70%]">
                  {post?.status && (
                    <span
                      className={clsx(
                        "font-mono border px-1 py-px rounded-md text-gray-600 dark:text-gray-400 shadow-[0_1px_2px_rgba(0,0,0,0.08)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.3)] text-xs",
                        post.status === "Active"
                          ? "border-green-500 dark:bg-green-500/30 dark:border-green-800 dark:text-green-200 bg-green-100 text-green-700"
                          : "border-gray-200 dark:border-gray-700"
                      )}
                    >
                      {post.status}
                    </span>
                  )}
                  {post?.statusText?.length
                    ? post.statusText.map((status) => (
                        <span
                          key={status}
                          className="font-mono border px-1 py-px rounded-md text-gray-600 dark:text-gray-400 shadow-[0_1px_2px_rgba(0,0,0,0.08)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.3)] text-xs border-gray-200 dark:border-gray-700"
                        >
                          {status}
                        </span>
                      ))
                    : ""}
                </div>
              </article>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
